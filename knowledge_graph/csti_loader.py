
import json
from collections import defaultdict
from pathlib import Path

from knowledge_graph.neo4j_connection import Neo4jConnection
from knowledge_graph.schema import NODE_LABELS, RELATIONSHIPS


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data/processed/csti_entities.json"

BATCH_SIZE = 500
SOURCE_NAME = "CTI Dataset (STIX 2.1)"


def load_json():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def write_batch(tx, query, rows):
    tx.run(query, rows=rows).consume()


def process_batches(session, query, records):
    """Write records in batches and return the number processed."""

    processed = 0

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]

        session.execute_write(
            write_batch,
            query,
            batch
        )

        processed += len(batch)

    return processed


def load_csti_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"CSTI input file not found: {INPUT_FILE}"
        )

    data = load_json()

    entities = data.get("entities", [])
    relationships = data.get("relationships", [])
    evidence = data.get("evidence", [])

    print("Starting CSTI / STIX import...")
    print(f"Entities: {len(entities)}")
    print(f"Relationships: {len(relationships)}")
    print(f"Evidence: {len(evidence)}")

    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        with connection.driver.session() as session:

            # ------------------------------------------------
            # 1. Create entity nodes
            # ------------------------------------------------

            entities_by_label = defaultdict(list)
            entity_labels = {}

            for entity in entities:

                entity_id = entity.get("id")
                label = entity.get("type")

                if not entity_id:
                    raise ValueError(
                        "CSTI entity is missing its ID."
                    )

                if label not in NODE_LABELS:
                    raise ValueError(
                        f"Unsupported CSTI entity label: {label}"
                    )

                entity_labels[entity_id] = label

                properties = dict(entity)
                properties["source"] = SOURCE_NAME

                entities_by_label[label].append(properties)

            entity_count = 0

            for label, records in entities_by_label.items():

                query = f"""
                UNWIND $rows AS row
                MERGE (n:{label} {{id: row.id}})
                SET n += row
                """

                entity_count += process_batches(
                    session,
                    query,
                    records
                )

                print(
                    f"Imported {len(records)} {label} nodes."
                )

            # ------------------------------------------------
            # 2. Create STIX relationships
            # ------------------------------------------------

            relationships_by_type = defaultdict(list)
            skipped_relationships = 0

            for relationship in relationships:

                source_id = relationship.get("source_ref")
                target_id = relationship.get("target_ref")
                rel_type = relationship.get("relationship")

                source_label = entity_labels.get(source_id)
                target_label = entity_labels.get(target_id)

                if (
                    not source_label
                    or not target_label
                    or rel_type not in RELATIONSHIPS
                ):
                    skipped_relationships += 1
                    continue

                properties = dict(relationship)

                properties["source"] = SOURCE_NAME

                relationships_by_type[
                    (source_label, rel_type, target_label)
                ].append({
                    "id": relationship["id"],
                    "source_id": source_id,
                    "target_id": target_id,
                    "properties": properties
                })

            relationship_count = 0

            for (
                source_label,
                rel_type,
                target_label
            ), records in relationships_by_type.items():

                query = f"""
                UNWIND $rows AS row

                MATCH (source:{source_label} {{id: row.source_id}})
                MATCH (target:{target_label} {{id: row.target_id}})

                MERGE (source)-[r:{rel_type} {{id: row.id}}]->(target)

                SET r += row.properties
                """

                relationship_count += process_batches(
                    session,
                    query,
                    records
                )

            # ------------------------------------------------
            # 3. Create Evidence nodes
            # ------------------------------------------------

            evidence_records = []

            for item in evidence:

                evidence_id = item.get("id")
                entity_id = item.get("entity_id")

                if not evidence_id or not entity_id:
                    raise ValueError(
                        "Evidence record is missing its ID "
                        "or entity_id."
                    )

                properties = dict(item)
                properties["source"] = SOURCE_NAME

                evidence_records.append(properties)

            evidence_query = """
            UNWIND $rows AS row

            MERGE (e:Evidence {id: row.id})

            SET e += row
            """

            evidence_count = process_batches(
                session,
                evidence_query,
                evidence_records
            )

            # ------------------------------------------------
            # 4. Link Evidence to its entity
            # ------------------------------------------------

            evidence_by_label = defaultdict(list)
            skipped_evidence_links = 0

            for item in evidence:

                entity_id = item.get("entity_id")
                label = entity_labels.get(entity_id)

                if not label:
                    skipped_evidence_links += 1
                    continue

                evidence_by_label[label].append({
                    "entity_id": entity_id,
                    "evidence_id": item["id"],
                    "link_id": "SUPPORTED_BY-" + item["id"],
                    "source": SOURCE_NAME
                })

            evidence_link_count = 0

            for label, records in evidence_by_label.items():

                query = f"""
                UNWIND $rows AS row

                MATCH (entity:{label} {{id: row.entity_id}})
                MATCH (e:Evidence {{id: row.evidence_id}})

                MERGE (entity)-[r:SUPPORTED_BY {{id: row.link_id}}]->(e)

                SET r.source = row.source
                """

                evidence_link_count += process_batches(
                    session,
                    query,
                    records
                )

            # ------------------------------------------------
            # 5. Print import summary
            # ------------------------------------------------

            print("\nCSTI IMPORT SUMMARY")
            print("-------------------")
            print(f"Entity nodes processed: {entity_count}")
            print(
                f"Relationships processed: {relationship_count}"
            )
            print(f"Evidence nodes processed: {evidence_count}")
            print(
                f"Evidence links processed: {evidence_link_count}"
            )
            print(
                f"Skipped relationships: {skipped_relationships}"
            )
            print(
                f"Skipped evidence links: {skipped_evidence_links}"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    load_csti_data()
