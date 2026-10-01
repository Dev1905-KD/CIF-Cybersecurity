from agents.graph_agent import GraphAgent


def main():

    agent = GraphAgent()

    answer = """
    CVE-2026-0544 is a security flaw discovered
    in itsourcecode School Management System 1.0.
    """

    result = agent.verify(
        answer
    )

    print("\nGraph Agent Result")
    print("=" * 50)

    print(
        "\nAgent:",
        result["agent"]
    )

    print(
        "Overall Status:",
        result["status"]
    )

    print(
        "Entities Checked:",
        result["entities_checked"]
    )

    print(
        "Entities Found:",
        result["entities_found"]
    )

    print("\nEntity Results:")
    print("-" * 50)

    for entity in result["entities"]:

        print(
            f"\nCVE: {entity['cve']}"
        )

        print(
            f"Exists in Graph: "
            f"{entity['exists']}"
        )

    agent.close()


if __name__ == "__main__":
    main()