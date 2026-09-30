from knowledge_graph.neo4j_connection import Neo4jConnection


class GraphRetriever:

    def __init__(self):
        self.connection = Neo4jConnection()

    def retrieve_cve_context(self, cve):

        query = """
        MATCH (v:Vulnerability {id: $cve})

        OPTIONAL MATCH (v)-[:AFFECTS]->(p:Product)

        OPTIONAL MATCH (v)-[:SUPPORTED_BY]->(e:Evidence)

        RETURN
            v.id AS cve,
            v.description AS description,

            collect(DISTINCT {
                vendor: p.vendor,
                product: p.name
            }) AS products,

            collect(DISTINCT {
                source: e.source,
                type: e.evidence_type,
                claim: e.claim,
                date_added: e.date_added
            }) AS evidence
        """

        with self.connection.driver.session() as session:

            result = session.run(
                query,
                cve=cve
            )

            record = result.single()

            if not record:
                return None

            return {
                "cve": record["cve"],
                "description": record["description"],
                "products": record["products"],
                "evidence": record["evidence"]
            }

    def close(self):
        self.connection.close()