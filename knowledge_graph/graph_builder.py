from knowledge_graph.neo4j_connection import Neo4jConnection


class GraphBuilder:

    def __init__(self):
        self.connection = Neo4jConnection()

    def create_vulnerability(
        self,
        vulnerability_id,
        description,
        source="NVD"
    ):

        query = """
        MERGE (v:Vulnerability {id: $id})
        SET v.description = $description,
            v.source = $source
        RETURN v
        """

        with self.connection.driver.session() as session:
            session.run(
                query,
                id=vulnerability_id,
                description=description,
                source=source
            )

    def close(self):
        self.connection.close()