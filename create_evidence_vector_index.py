from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

query = """
CREATE VECTOR INDEX evidence_embedding_index IF NOT EXISTS
FOR (e:Evidence) ON (e.embedding)
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 768,
        `vector.similarity_function`: 'cosine'
    }
}
"""

try:
    with driver.session() as session:
        session.run(query).consume()
        print("Evidence vector index created or already exists.")
        for record in session.run(
            "SHOW INDEXES YIELD name, type, state WHERE name = 'evidence_embedding_index' RETURN name, type, state"
        ):
            print(dict(record))
finally:
    driver.close()
