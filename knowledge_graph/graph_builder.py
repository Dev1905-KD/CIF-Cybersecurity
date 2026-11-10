
from knowledge_graph.neo4j_connection import Neo4jConnection
from knowledge_graph.schema import NODE_LABELS, RELATIONSHIPS


class GraphBuilder:

    def __init__(self):
        self.connection = Neo4jConnection()

    def create_node(self, label, properties):

        if label not in NODE_LABELS:
            raise ValueError(f"Unsupported node label: {label}")

        if not properties.get("id"):
            raise ValueError("Node properties must contain a valid id")

        query = f"""
        MERGE (n:{label} {{id: $id}})
        ON CREATE SET n += $properties
        ON MATCH SET n += $update_properties
        """

        update_properties = {
            key: value
            for key, value in properties.items()
            if key != "source"
        }

        with self.connection.driver.session() as session:
            session.run(
                query,
                id=properties["id"],
                properties=properties,
                update_properties=update_properties
            )

    def create_relationship(
        self,
        source_id,
        source_label,
        relationship,
        target_id,
        target_label,
        source="system",
        properties=None
    ):

        if source_label not in NODE_LABELS:
            raise ValueError(
                f"Unsupported source label: {source_label}"
            )

        if target_label not in NODE_LABELS:
            raise ValueError(
                f"Unsupported target label: {target_label}"
            )

        if relationship not in RELATIONSHIPS:
            raise ValueError(
                f"Unsupported relationship type: {relationship}"
            )

        if not source_id or not target_id:
            raise ValueError(
                "Relationship endpoints must have valid IDs"
            )

        query = f"""
        MATCH (source:{source_label} {{id: $source_id}})
        MATCH (target:{target_label} {{id: $target_id}})
        MERGE (source)-[r:{relationship}]->(target)
        SET r.source = $source
        SET r += $properties
        """

        with self.connection.driver.session() as session:
            session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                source=source,
                properties=properties or {}
            )

    def close(self):
        self.connection.close()
