from claim_verification.verifier import (
    ClaimVerifier
)


class EvidenceAgent:

    def __init__(self):

        self.verifier = ClaimVerifier()

    def verify(
        self,
        answer,
        evidence
    ):

        results = self.verifier.verify_claims(
            answer,
            evidence
        )

        supported = 0
        partial = 0
        unsupported = 0

        for result in results:

            status = result["status"]

            if status == "Supported":
                supported += 1

            elif status == "Partially Supported":
                partial += 1

            elif status == "Unsupported":
                unsupported += 1

        total = len(results)

        if total == 0:

            overall_status = "No claims"

        elif unsupported > 0:

            overall_status = "Needs Review"

        elif partial > 0:

            overall_status = "Partially Supported"

        else:

            overall_status = "Supported"

        return {
            "agent": "Evidence Agent",
            "status": overall_status,
            "total_claims": total,
            "supported": supported,
            "partially_supported": partial,
            "unsupported": unsupported,
            "claims": results
        }