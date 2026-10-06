import re

from hypotheses.hypothesis import Hypothesis


class HypothesisGenerator:

    # ---------------------------------
    # Generate hypotheses from a
    # verified investigation result
    # ---------------------------------

    def generate(
        self,
        query: str,
        answer: str,
        consensus_result: dict,
        beliefs: list
    ):

        hypotheses = []

        cves = self._extract_cves(
            query + "\n" + answer
        )

        if not cves:
            return hypotheses

        consensus_status = consensus_result.get(
            "status",
            "Needs Review"
        )

        for cve in cves:

            belief_ids = [
                belief.belief_id
                for belief in beliefs
                if cve in belief.entity_ids
            ]

            hypothesis_id = (
                f"hypothesis-{cve.lower()}-investigation"
            )

            statement = (
                f"{cve} should be considered "
                f"relevant to the current cybersecurity "
                f"investigation."
            )

            if consensus_status == "Verified":
                status = "supported"
                verification_status = "verified"

            elif consensus_status == "Inconsistent":
                status = "needs_review"
                verification_status = "inconsistent"

            else:
                status = "proposed"
                verification_status = "needs_review"

            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                statement=statement,
                status=status,
                entity_ids=[cve],
                belief_ids=belief_ids,
                verification_status=verification_status,
                metadata={
                    "consensus_status":
                        consensus_status
                }
            )

            hypotheses.append(
                hypothesis
            )

        return hypotheses

    # ---------------------------------
    # Extract CVE identifiers
    # ---------------------------------

    def _extract_cves(
        self,
        text: str
    ):

        return list(
            dict.fromkeys(
                re.findall(
                    r"CVE-\d{4}-\d{4,7}",
                    text.upper()
                )
            )
        )