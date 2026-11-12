
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.vector_retriever import VectorRetriever


def main():
    query = input("Enter a cybersecurity query: ").strip()

    if not query:
        raise SystemExit("A query is required.")

    retriever = VectorRetriever(top_k=5)

    try:
        results = retriever.retrieve(query)

        print(f"\nRetrieved {len(results)} evidence records.\n")

        for i, item in enumerate(results, 1):
            print(f"{i}. Similarity: {item.get('similarity', 0):.4f}")
            print(f"   Evidence ID: {item.get('id')}")
            print(f"   Source: {item.get('source')}")
            print(f"   Source type: {item.get('source_type')}")
            print(f"   STIX type: {item.get('stix_type')}")
            print(f"   Confidence: {item.get('confidence')}")
            print(f"   Entity ID: {item.get('entity_id')}")
            print(f"   Reference: {item.get('reference')}")
            print(f"   Timestamp: {item.get('timestamp')}")
            print(f"   Claim: {item.get('claim')}")
            print(f"   Entities: {item.get('entities')}")
            print()

    finally:
        retriever.close()


if __name__ == "__main__":
    main()
