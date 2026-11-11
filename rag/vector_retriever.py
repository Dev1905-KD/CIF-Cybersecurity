import os
import requests

from dotenv import load_dotenv
from knowledge_graph.neo4j_connection import Neo4jConnection


load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
).rstrip("/")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)
VECTOR_INDEX_NAME = os.getenv(
    "NEO4J_VECTOR_INDEX",
    "evidence_embedding_index"
)
VECTOR_DIMENSIONS = 768


class VectorRetriever:

    def __init__(self, top_k=8):
        self.top_k = top_k
        self.connection = Neo4jConnection()

    def embed_query(self, query):
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": EMBEDDING_MODEL,
                "input": query
            },
            timeout=120
        )
        response.raise_for_status()

        embeddings = response.json().get("embeddings", [])

        if not embeddings:
            raise RuntimeError("Ollama returned no query embedding.")

        embedding = embeddings[0]

        if len(embedding) != VECTOR_DIMENSIONS:
            raise RuntimeError(
                f"Expected {VECTOR_DIMENSIONS} dimensions, "
                f"received {len(embedding)}."
            )

        return embedding

    def retrieve(self, query, top_k=None):
        embedding = self.embed_query(query)

        cypher = """
        CALL db.index.vector.queryNodes(
            $index_name,
            $top_k,
            $embedding
        )
        YIELD node, score

        OPTIONAL MATCH (entity)-[:SUPPORTED_BY]->(node)

        WITH node, score,
             collect(DISTINCT CASE
                 WHEN entity IS NULL THEN null
                 ELSE {
                     id: entity.id,
                     name: entity.name,
                     labels: labels(entity),
                     source: entity.source
                 }
             END) AS related_entities

        RETURN
            node.id AS id,
            node.source AS source,
            node.evidence_type AS evidence_type,
            node.claim AS claim,
            node.date_added AS date_added,
            score AS similarity,
            [item IN related_entities WHERE item IS NOT NULL]
                AS entities
        ORDER BY similarity DESC
        """

        with self.connection.driver.session() as session:
            records = session.run(
                cypher,
                index_name=VECTOR_INDEX_NAME,
                top_k=top_k or self.top_k,
                embedding=embedding
            )

            return [dict(record) for record in records]

    def close(self):
        self.connection.close()
