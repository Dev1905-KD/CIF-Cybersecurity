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

    # ---------------------------------
    # Retrieval Status
    # ---------------------------------

    print(
        "\nRetrieval Status:",
        result.get("status")
    )

    print(
        "Evidence Status:",
        result.get("evidence_status")
    )

    # ---------------------------------
    # Existing Claim Verification
    # ---------------------------------

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

    # ---------------------------------
    # Multi-Agent Verification
    # ---------------------------------

    print("\nMulti-Agent Verification:")
    print("=" * 60)

    multi_agent = result.get(
        "multi_agent_verification",
        {}
    )

    # ---------------------------------
    # Evidence Agent
    # ---------------------------------

    evidence_agent = multi_agent.get(
        "evidence_agent",
        {}
    )

    print("\nEvidence Agent")
    print("-" * 60)

    print(
        "Status:",
        evidence_agent.get("status")
    )

    print(
        "Total Claims:",
        evidence_agent.get("total_claims")
    )

    print(
        "Supported:",
        evidence_agent.get("supported")
    )

    print(
        "Partially Supported:",
        evidence_agent.get(
            "partially_supported"
        )
    )

    print(
        "Unsupported:",
        evidence_agent.get(
            "unsupported"
        )
    )

    # ---------------------------------
    # Graph Agent
    # ---------------------------------

    graph_agent = multi_agent.get(
        "graph_agent",
        {}
    )

    print("\nGraph Agent")
    print("-" * 60)

    print(
        "Status:",
        graph_agent.get("status")
    )

    print(
        "Entities Checked:",
        graph_agent.get(
            "entities_checked"
        )
    )

    print(
        "Entities Found:",
        graph_agent.get(
            "entities_found"
        )
    )

    for entity in graph_agent.get(
        "entities",
        []
    ):

        print(
            f"CVE: {entity.get('cve')}"
        )

        print(
            f"Exists in Graph: "
            f"{entity.get('exists')}"
        )

    # ---------------------------------
    # Consistency Agent
    # ---------------------------------

    consistency_agent = multi_agent.get(
        "consistency_agent",
        {}
    )

    print("\nConsistency Agent")
    print("-" * 60)

    print(
        "Status:",
        consistency_agent.get("status")
    )

    checks = consistency_agent.get(
        "checks",
        {}
    )

    for check, value in checks.items():

        print(
            f"{check}: {value}"
        )

    findings = consistency_agent.get(
        "findings",
        []
    )

    if findings:

        print("\nFindings:")

        for finding in findings:

            print(
                f"- {finding.get('type')}: "
                f"{finding.get('message')}"
            )

    else:

        print(
            "No consistency issues detected."
        )

    # ---------------------------------
    # Consensus Agent
    # ---------------------------------

    consensus = multi_agent.get(
        "consensus",
        {}
    )

    print("\nConsensus Agent")
    print("-" * 60)

    print(
        "Final Status:",
        consensus.get("status")
    )

    verification = consensus.get(
        "verification",
        {}
    )

    print("\nVerification:")

    for agent_name, status in (
        verification.items()
    ):

        print(
            f"{agent_name}: {status}"
        )

    conflicts = consensus.get(
        "conflicts",
        []
    )

    if conflicts:

        print("\nConflicts:")

        for conflict in conflicts:

            print(
                f"- {conflict.get('type')}: "
                f"{conflict.get('message')}"
            )

    else:

        print(
            "\nNo verification conflicts detected."
        )

    # ---------------------------------
    # Llama Answer
    # ---------------------------------

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