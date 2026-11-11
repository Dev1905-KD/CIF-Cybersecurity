import os
import hashlib
import requests
from datetime import datetime, timezone

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text"
BATCH_SIZE = 128

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def build_embedding_text(record):
    parts = [
        f"Evidence source: {clean(record.get('source'))}",
        f"Evidence type: {clean(record.get('evidence_type'))}",
        f"Evidence claim: {clean(record.get('claim'))}",
        f"Date added: {clean(record.get('date_added'))}",
        f"Required action: {clean(record.get('required_action'))}",
        f"Known ransomware use: {clean(record.get('known_ransomware_use'))}",
    ]

    entities = record.get("entities") or []

    for entity in sorted(
        entities,
        key=lambda item: clean(item.get("id"))
    ):
        details = [
            f"Entity type: {', '.join(entity.get('labels') or [])}",
            f"Entity ID: {clean(entity.get('id'))}",
            f"Entity name: {clean(entity.get('name'))}",
            f"Entity description: {clean(entity.get('description'))}",
            f"Entity source: {clean(entity.get('source'))}",
            f"STIX type: {clean(entity.get('stix_type'))}",
            f"Entity type detail: {clean(entity.get('type'))}",
        ]
        parts.extend(item for item in details if item.split(": ", 1)[1])

    return "\n".join(part for part in parts if part.split(": ", 1)[1])


def get_embeddings(texts):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": texts
        },
        timeout=180
    )
    response.raise_for_status()

    embeddings = response.json()["embeddings"]

    if len(embeddings) != len(texts):
        raise RuntimeError("Ollama returned an unexpected number of embeddings.")

    if any(len(vector) != 768 for vector in embeddings):
        raise RuntimeError("An embedding did not contain 768 dimensions.")

    return embeddings


def main():
    last_id = ""
    processed = 0
    skipped = 0

    read_query = """
    MATCH (e:Evidence)
    WHERE e.id > $last_id
    OPTIONAL MATCH (n)-[:SUPPORTED_BY]->(e)
    WITH e, collect(DISTINCT {
        labels: labels(n),
        id: n.id,
        name: n.name,
        description: n.description,
        source: n.source,
        stix_type: n.stix_type,
        type: n.type
    }) AS entities
    RETURN
        e.id AS id,
        e.claim AS claim,
        e.source AS source,
        e.evidence_type AS evidence_type,
        e.date_added AS date_added,
        e.required_action AS required_action,
        e.known_ransomware_use AS known_ransomware_use,
        e.embedding_text_hash AS embedding_text_hash,
        e.embedding_model AS embedding_model,
        entities
    ORDER BY e.id
    LIMIT $batch_size
    """

    write_query = """
    UNWIND $rows AS row
    MATCH (e:Evidence {id: row.id})
    SET
        e.embedding = row.embedding,
        e.embedding_model = row.embedding_model,
        e.embedding_text_hash = row.embedding_text_hash,
        e.embedding_updated_at = row.embedding_updated_at
    """

    try:
        while True:
            with driver.session() as session:
                records = list(session.run(
                    read_query,
                    last_id=last_id,
                    batch_size=BATCH_SIZE
                ))

            if not records:
                break

            rows_to_embed = []

            for record in records:
                data = dict(record)
                last_id = data["id"]

                text = build_embedding_text(data)
                text_hash = hashlib.sha256(
                    text.encode("utf-8")
                ).hexdigest()

                if (
                    data.get("embedding_text_hash") == text_hash
                    and data.get("embedding_model") == EMBEDDING_MODEL
                ):
                    skipped += 1
                    continue

                rows_to_embed.append({
                    "id": data["id"],
                    "text": text,
                    "embedding_text_hash": text_hash
                })

            if rows_to_embed:
                texts = [row["text"] for row in rows_to_embed]
                embeddings = get_embeddings(texts)

                timestamp = datetime.now(
                    timezone.utc
                ).isoformat()

                updates = []

                for row, embedding in zip(rows_to_embed, embeddings):
                    updates.append({
                        "id": row["id"],
                        "embedding": embedding,
                        "embedding_model": EMBEDDING_MODEL,
                        "embedding_text_hash": row["embedding_text_hash"],
                        "embedding_updated_at": timestamp
                    })

                with driver.session() as session:
                    session.execute_write(
                        lambda tx: tx.run(
                            write_query,
                            rows=updates
                        ).consume()
                    )

                processed += len(updates)

            print(
                f"Embedded: {processed} | "
                f"Already current: {skipped} | "
                f"Last evidence ID: {last_id}"
            )

        print("\nEmbedding indexing finished.")
        print(f"New or updated embeddings: {processed}")
        print(f"Already up to date: {skipped}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
