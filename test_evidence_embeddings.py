from dotenv import load_dotenv
import os

from neo4j import GraphDatabase
from rag.embedding_indexer import build_embedding_text, get_embeddings

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

query = """
MATCH (n)-[:SUPPORTED_BY]->(e:Evidence)
WITH e, collect(DISTINCT {
    labels: labels(n),
    id: n.id,
    name: n.name,
    description: n.description,
    source: n.source,
    stix_type: n.stix_type,
    type: n.type
}) AS entities
WITH e, entities
ORDER BY e.source
WITH e.source AS source, collect({
    id: e.id,
    claim: e.claim,
    evidence_type: e.evidence_type,
    date_added: e.date_added,
    required_action: e.required_action,
    known_ransomware_use: e.known_ransomware_use,
    entities: entities
})[0] AS sample
RETURN source, sample
ORDER BY source
"""

try:
    with driver.session() as session:
        records = list(session.run(query))

    samples = [dict(record["sample"]) for record in records]
    texts = [build_embedding_text(sample) for sample in samples]
    embeddings = get_embeddings(texts)

    for record, text, embedding in zip(records, texts, embeddings):
        print(
            f"Source: {record['source']} | "
            f"Evidence ID: {record['sample']['id']} | "
            f"Text length: {len(text)} | "
            f"Embedding dimensions: {len(embedding)}"
        )

    print("Read-only embedding test passed. No graph data was changed.")

finally:
    driver.close()
