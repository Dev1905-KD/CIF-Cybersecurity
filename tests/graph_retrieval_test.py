from rag.graph_retriever import GraphRetriever


cve = input("Enter CVE ID: ")

retriever = GraphRetriever()

try:

    result = retriever.retrieve_cve_context(
        cve
    )

    print("\nRetrieved Context:\n")
    print(result)

finally:
    retriever.close()
    