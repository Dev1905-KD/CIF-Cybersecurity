from knowledge_graph.neo4j_connection import Neo4jConnection


connection = Neo4jConnection()

try:
    connection.verify_connection()
finally:
    connection.close()