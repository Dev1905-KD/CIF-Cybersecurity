from knowledge_graph.neo4j_connection import Neo4jConnection


class GraphBuilder:

    def __init__(self):
        self.connection = Neo4jConnection()

    def create_node(self, label, properties):
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $properties
        """

        with self.connection.driver.session() as session:
            session.run(
                query,
                id=properties["id"],
                properties=properties
            )

    def create_relationship(
        self,
        source_id,
        source_label,
        relationship,
        target_id,
        target_label,
        source="system"
    ):

        query = f"""
        MATCH (source:{source_label} {{id: $source_id}})
        MATCH (target:{target_label} {{id: $target_id}})
        MERGE (source)-[r:{relationship}]->(target)
        SET r.source = $source
        """

        with self.connection.driver.session() as session:
            session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                source=source
        )

    def close(self):
        self.connection.close()