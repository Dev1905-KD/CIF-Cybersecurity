from rag.crag_llama_pipeline import (
    CRAGLlamaPipeline
)


pipeline = CRAGLlamaPipeline()

try:

    query = input(
        "\nAsk a cybersecurity question: "
    )

    result = pipeline.run(
        query
    )

    print("\n")
    print("=" * 60)
    print("CIF CYBERSECURITY INTELLIGENCE")
    print("=" * 60)

    print(
        "\nRetrieval Status:",
        result.get("status")
    )
    print(
    "Evidence Status:",
    result.get("evidence_status")
    )
    print("\nClaim Verification:")
    print("-" * 60)

    claim_results = result.get(
        "claim_verification",
        []
    )
    for item in claim_results:

        print(
            f"\nClaim: {item['claim']}"
        )

        print(
            f"Status: {item['status']}"
        )
    if result.get("answer"):

        print("\nLlama Answer:")
        print("-" * 60)
        print(result["answer"])

    else:

        print(
            "\nMessage:",
            result.get("message")
        )

finally:

    pipeline.close()