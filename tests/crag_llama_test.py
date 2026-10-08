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

    # ---------------------------------
    # Persistent World State
    # ---------------------------------

    world_state = pipeline.get_world_state()

    print("\nPersistent World State:")
    print("=" * 60)

    print(
        "State Version:",
        world_state.version
    )

    print(
        "Entities:",
        len(world_state.entities)
    )

    print(
        "Evidence Records:",
        len(world_state.evidence)
    )

    print(
        "Beliefs:",
        len(world_state.beliefs)
    )

    print(
        "Hypotheses:",
        len(world_state.hypotheses)
    )

    print(
        "Verification History:",
        len(
            world_state.verification_history
        )
    )

    print(
        "Simulation Records:",
        len(
            world_state.simulation_history
        )
    )

    # ---------------------------------
    # Belief Graph
    # ---------------------------------

    print()
    print("Belief Graph:")
    print("=" * 60)

    for belief in result.get(
        "beliefs",
        []
    ):

        print(
            f"Belief ID: "
            f"{belief['belief_id']}"
        )

        print(
            f"Claim: "
            f"{belief['claim']}"
        )

        print(
            f"Status: "
            f"{belief['status']}"
        )

        print(
            f"Entities: "
            f"{belief['entity_ids']}"
        )

        print(
            f"Verification: "
            f"{belief['verification_status']}"
        )

        print()

    # ---------------------------------
    # Hypothesis Generation
    # ---------------------------------

    print()
    print("Hypothesis Generation:")
    print("=" * 60)

    for hypothesis in result.get(
        "hypotheses",
        []
    ):

        print(
            f"Hypothesis ID: "
            f"{hypothesis['hypothesis_id']}"
        )

        print(
            f"Statement: "
            f"{hypothesis['statement']}"
        )

        print(
            f"Status: "
            f"{hypothesis['status']}"
        )

        print(
            f"Entities: "
            f"{hypothesis['entity_ids']}"
        )

        print(
            f"Belief IDs: "
            f"{hypothesis['belief_ids']}"
        )

        print(
            f"Verification: "
            f"{hypothesis['verification_status']}"
        )

        print()

    # ---------------------------------
    # Hypothesis Evaluation
    # ---------------------------------

    print()
    print("Hypothesis Evaluation:")
    print("=" * 60)

    for evaluation in result.get(
        "hypothesis_evaluations",
        []
    ):

        print(
            f"Hypothesis ID: "
            f"{evaluation['hypothesis_id']}"
        )

        print(
            f"Evaluation Status: "
            f"{evaluation['evaluation_status']}"
        )

        print(
            f"Reason: "
            f"{evaluation['reason']}"
        )

        print(
            f"Simulation Scenario: "
            f"{evaluation['simulation_scenario_id']}"
        )

        print(
            f"Outcome Count: "
            f"{evaluation['outcome_count']}"
        )

        print(
            f"Simulation Completed: "
            f"{evaluation['simulation_completed']}"
        )

        print()

    # ---------------------------------
    # Belief Revisions
    # ---------------------------------

    print()
    print("Belief Revisions:")
    print("=" * 60)

    for revision in result.get(
        "belief_revisions",
        []
    ):

        print(
            f"Belief ID: "
            f"{revision['belief_id']}"
        )

        print(
            f"Previous Status: "
            f"{revision['previous_status']}"
        )

        print(
            f"New Status: "
            f"{revision['new_status']}"
        )

        print(
            f"Revision Type: "
            f"{revision['revision_type']}"
        )

        print(
            f"Reason: "
            f"{revision['reason']}"
        )

        print(
            f"Evidence IDs: "
            f"{revision['evidence_ids']}"
        )

        print(
            f"Timestamp: "
            f"{revision['timestamp']}"
        )

        print()

    # ---------------------------------
    # Simulation
    # ---------------------------------

    simulation = result.get(
        "simulation"
    )

    if simulation:

        print()
        print("Simulation:")
        print("=" * 60)

        print(
            f"Scenario ID: "
            f"{simulation['scenario_id']}"
        )

        print("\nInitial State:")
        print(
            simulation["initial_state"]
        )

        print("\nSimulation Events:")

        for event in simulation.get(
            "events",
            []
        ):

            print(
                event
            )

        print("\nSimulation Outcomes:")

        for outcome in simulation.get(
            "outcomes",
            []
        ):

            print(
                outcome
            )

        print("\nFinal State:")
        print(
            simulation["final_state"]
        )

    # ---------------------------------
    # Decision Engine
    # ---------------------------------

    decision = result.get(
        "decision",
        {}
    )

    print()
    print("Decision Engine:")
    print("=" * 60)

    if decision:

        print(
            "Decision ID:",
            decision.get("decision_id")
        )

        print(
            "Status:",
            decision.get("status")
        )

        print(
            "Risk Level:",
            decision.get("risk_level")
        )

        print(
            "Rationale:",
            decision.get("rationale")
        )

        print(
            "Verification Status:",
            decision.get("verification_status")
        )

        print(
            "Hypothesis Status:",
            decision.get("hypothesis_status")
        )

        print(
            "Simulation Status:",
            decision.get("simulation_status")
        )

        print("\nRecommended Actions:")

        for action in decision.get(
            "recommended_actions",
            []
        ):

            print(
                f"- {action}"
            )

        print("\nSupporting Evidence:")

        for evidence in decision.get(
            "supporting_evidence",
            []
        ):

            print(
                f"- {evidence}"
            )

        metadata = decision.get(
            "metadata",
            {}
        )

        if metadata:

            print("\nDecision Metadata:")

            for key, value in metadata.items():

                print(
                    f"{key}: {value}"
                )

    else:

        print(
            "No decision was returned by "
            "the Decision Engine."
        )

finally:

    pipeline.close()