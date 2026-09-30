from knowledge_graph.neo4j_connection import Neo4jConnection


query = """
MATCH (v:Vulnerability {id: $cve})
OPTIONAL MATCH (v)-[:SUPPORTED_BY]->(e:Evidence)
OPTIONAL MATCH (v)-[:AFFECTS]->(p:Product)

RETURN
    v.id AS cve,
    v.description AS description,
    collect(DISTINCT e.source) AS evidence_sources,
    collect(DISTINCT p.name) AS products
"""


cve = input("Enter CVE ID: ")

connection = Neo4jConnection()

try:

    with connection.driver.session() as session:

        result = session.run(
            query,
            cve=cve
        )

        record = result.single()

        if record:
            print("\nCVE:", record["cve"])
            print(
                "Description:",
                record["description"]
            )
            print(
                "Evidence:",
                record["evidence_sources"]
            )
            print(
                "Products:",
                record["products"]
            )
        else:
            print("CVE not found.")

finally:
    connection.close()