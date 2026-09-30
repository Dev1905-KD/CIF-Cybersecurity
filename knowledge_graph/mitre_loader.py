import json
from pathlib import Path

from knowledge_graph.graph_builder import GraphBuilder


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR /
    "data/processed/mitre_entities.json"
)


TYPE_MAPPING = {
    "attack-pattern": "Technique",
    "intrusion-set": "ThreatActor",
    "malware": "Malware",
    "tool": "Tool",
    "campaign": "Campaign"
}


RELATIONSHIP_MAPPING = {
    "uses": "USES",
    "targets": "TARGETS",
    "exploits": "EXPLOITS",
    "attributed-to": "ASSOCIATED_WITH",
    "associated-with": "ASSOCIATED_WITH",
    "mitigates": "MITIGATES",
    "detects": "DETECTS",
    "subtechnique-of": "SUBTECHNIQUE_OF"
}


def load_mitre_data():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    builder = GraphBuilder()

    try:

        # -------------------------
        # Create entity nodes
        # -------------------------

        for entity in data.get("entities", []):

            entity_type = entity.get("type")

            label = TYPE_MAPPING.get(entity_type)

            if not label:
                continue

            properties = {
                "id": entity.get("id"),
                "name": entity.get("name", ""),
                "description": entity.get(
                    "description",
                    ""
                ),
                "source": "MITRE ATT&CK"
            }

            builder.create_node(
                label,
                properties
            )

        # -------------------------
        # Create relationships
        # -------------------------

        for relationship in data.get(
            "relationships",
            []
        ):

            relationship_type = relationship.get(
                "relationship"
            )

            neo4j_relationship = (
                RELATIONSHIP_MAPPING.get(
                    relationship_type
                )
            )

            if not neo4j_relationship:
                continue

            source_ref = relationship.get(
                "source_ref"
            )

            target_ref = relationship.get(
                "target_ref"
            )

            # Find labels based on entity IDs
            source_label = find_entity_label(
                data,
                source_ref
            )

            target_label = find_entity_label(
                data,
                target_ref
            )

            if not source_label or not target_label:
                continue

            builder.create_relationship(
                source_ref,
                source_label,
                neo4j_relationship,
                target_ref,
                target_label
            )

        print("MITRE Knowledge Graph loading completed.")

    finally:
        builder.close()


def find_entity_label(data, entity_id):

    for entity in data.get("entities", []):

        if entity.get("id") == entity_id:

            return TYPE_MAPPING.get(
                entity.get("type")
            )

    return None


if __name__ == "__main__":
    load_mitre_data()