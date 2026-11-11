from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

try:
    with driver.session() as session:
        result = session.run(
            "SHOW PROCEDURES YIELD name RETURN name ORDER BY name"
        )
        for record in result:
            if record["name"].startswith("db.index.vector"):
                print(record["name"])
finally:
    driver.close()
