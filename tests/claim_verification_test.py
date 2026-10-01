from claim_verification.verifier import ClaimVerifier


def main():

    verifier = ClaimVerifier()

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

    results = verifier.verify_claims(
        answer,
        evidence
    )

    print("\nClaim Verification Results")
    print("=" * 40)

    for result in results:

        print(
            f"\nClaim: {result['claim']}"
        )

        print(
            f"Status: {result['status']}"
        )


if __name__ == "__main__":
    main()