from rag.vector_retriever import VectorRetriever


def main():
    query = input("Enter a cybersecurity query: ").strip()

    if not query:
        raise SystemExit("A query is required.")

    retriever = VectorRetriever(top_k=5)

    try:
        results = retriever.retrieve(query)

        print(f"\nRetrieved {len(results)} evidence records.\n")

        for index, item in enumerate(results, start=1):
            print(f"{index}. Similarity: {item.get('similarity', 0):.4f}")
            print(f"   Evidence ID: {item.get('id')}")
            print(f"   Source: {item.get('source')}")
            print(f"   Type: {item.get('evidence_type')}")
            print(f"   Claim: {item.get('claim')}")
            print(f"   Related entities: {item.get('entities')}")
            print()

    finally:
        retriever.close()


if __name__ == "__main__":
    main()
