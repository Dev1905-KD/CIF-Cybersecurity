from agents.consensus import (
    ConsensusAgent
)


def main():

    agent = ConsensusAgent()

    evidence_result = {
        "agent": "Evidence Agent",
        "status": "Supported",
        "total_claims": 2,
        "supported": 2,
        "partially_supported": 0,
        "unsupported": 0
    }

    graph_result = {
        "agent": "Graph Agent",
        "status": "Supported",
        "entities_checked": 1,
        "entities_found": 1
    }

    consistency_result = {
        "agent": "Consistency Agent",
        "status": "Consistent",
        "findings": []
    }

    result = agent.evaluate(
        evidence_result,
        graph_result,
        consistency_result
    )

    print("\nConsensus Agent Result")
    print("=" * 60)

    print(
        "\nAgent:",
        result["agent"]
    )

    print(
        "Final Status:",
        result["status"]
    )

    print("\nVerification:")
    print("-" * 60)

    for agent_name, status in (
        result["verification"].items()
    ):

        print(
            f"{agent_name}: {status}"
        )

    print("\nConflicts:")
    print("-" * 60)

    if not result["conflicts"]:

        print("No conflicts detected.")

    else:

        for conflict in result["conflicts"]:

            print(
                f"\nType: {conflict['type']}"
            )

            print(
                f"Message: {conflict['message']}"
            )


if __name__ == "__main__":
    main()