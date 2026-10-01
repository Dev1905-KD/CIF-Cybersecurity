from agents.consistency_agent import (
    ConsistencyAgent
)


def main():

    agent = ConsistencyAgent()

    answer = """
    CVE-2026-0544 affects itsourcecode School Management System 1.0.
    The vulnerability results in SQL injection.
    The evidence comes from NVD.
    """

    context = """
    CVE: CVE-2026-0544

    Description: A security flaw discovered in
    itsourcecode School Management System 1.0.

    Affected Products:
    - itsourcecode School Management System 1.0

    Evidence:
    - Source: NVD; Claim: Security flaw affecting
      itsourcecode School Management System 1.0.
    """

    result = agent.verify(
        answer,
        context
    )

    print("\nConsistency Agent Result")
    print("=" * 60)

    print(
        "\nAgent:",
        result["agent"]
    )

    print(
        "Overall Status:",
        result["status"]
    )

    print("\nChecks:")
    print("-" * 60)

    for check, status in result["checks"].items():

        print(
            f"{check}: {status}"
        )

    print("\nFindings:")
    print("-" * 60)

    if not result["findings"]:

        print("No consistency issues detected.")

    else:

        for finding in result["findings"]:

            print(
                f"\nType: {finding['type']}"
            )

            print(
                f"Severity: {finding['severity']}"
            )

            print(
                f"Message: {finding['message']}"
            )


if __name__ == "__main__":
    main()