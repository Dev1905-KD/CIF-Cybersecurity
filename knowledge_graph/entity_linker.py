from knowledge_graph.neo4j_connection import Neo4jConnection


class EntityLinker:

    def __init__(self):
        self.connection = Neo4jConnection()

    def link_vulnerabilities_to_evidence(self):

        query = """
        MATCH (v:Vulnerability)
        MATCH (e:Evidence)
        WHERE e.id = "KEV-" + v.id
        MERGE (v)-[:SUPPORTED_BY]->(e)
        """

        with self.connection.driver.session() as session:
            result = session.run(query)
            result.consume()

        print(
            "Vulnerability-Evidence linking completed."
        )

    def close(self):
        self.connection.close()


if __name__ == "__main__":

    linker = EntityLinker()

    try:
        linker.link_vulnerabilities_to_evidence()

    finally:
        linker.close()