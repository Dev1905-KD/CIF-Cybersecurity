from agents.evidence_agent import EvidenceAgent


def main():

    agent = EvidenceAgent()

    answer = """
    CVE-2026-0544 affects itsourcecode School Management System 1.0.
    The vulnerability results in SQL injection.
    The vulnerability affects Google Chrome.
    """

    evidence = """
    CVE-2026-0544 is a security flaw discovered in
    itsourcecode School Management System 1.0.
    The manipulation of the argument ID results in SQL injection.
    It is possible to launch the attack remotely.
    """

    result = agent.verify(
        answer,
        evidence
    )

    print("\nEvidence Agent Result")
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
        "Total Claims:",
        result["total_claims"]
    )

    print(
        "Supported:",
        result["supported"]
    )

    print(
        "Partially Supported:",
        result["partially_supported"]
    )

    print(
        "Unsupported:",
        result["unsupported"]
    )

    print("\nClaim Results:")
    print("-" * 50)

    for claim in result["claims"]:

        print(
            f"\nClaim: {claim['claim']}"
        )

        print(
            f"Status: {claim['status']}"
        )


if __name__ == "__main__":
    main()