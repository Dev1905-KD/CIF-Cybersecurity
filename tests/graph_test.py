from knowledge_graph.graph_builder import GraphBuilder


builder = GraphBuilder()

try:
    builder.create_vulnerability(
        "CVE-CIF-TEST-001",
        "Test vulnerability for CIF Knowledge Graph."
    )

    print("Test vulnerability created successfully.")

finally:
    builder.close()
    