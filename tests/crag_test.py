from rag.pipeline import CRAGPipeline


pipeline = CRAGPipeline()

try:

    query = input(
        "Ask a cybersecurity question: "
    )

    result = pipeline.run(
        query
    )

    print("\n==============================")
    print("CRAG RESULT")
    print("==============================")

    print(
        "\nCVE:",
        result.get("cve")
    )

    print(
        "\nRetrieval Status:",
        result.get("grading")
    )

    print(
        "\nCorrection Used:",
        result.get(
            "correction_used"
        )
    )

    print(
        "\nRetrieved Context:"
    )

    print(
        result.get("context")
    )

finally:

    pipeline.close()