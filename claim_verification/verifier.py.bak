import re


class ClaimVerifier:

    def verify_claims(self, answer, evidence):

        results = []

        claims = [
            line.strip()
            for line in answer.split("\n")
            if line.strip()
        ]

        evidence_lower = evidence.lower()

        for claim in claims:

            if claim.endswith(":"):
                continue

            status = self._verify_claim(
                claim,
                evidence_lower
            )

            results.append({
                "claim": claim,
                "status": status
            })

        return results

    def _verify_claim(self, claim, evidence_lower):

        claim_lower = claim.lower()

        # ---------------------------------
        # 1. Exact phrase match
        # ---------------------------------

        if claim_lower in evidence_lower:
            return "Supported"

        # ---------------------------------
        # 2. Source verification
        # ---------------------------------

        source_patterns = [
            ("nvd", "source: nvd"),
            ("cisa", "source: cisa"),
            ("mitre", "source: mitre")
        ]

        for source, evidence_source in source_patterns:

            if source in claim_lower and evidence_source in evidence_lower:
                return "Supported"

        # ---------------------------------
        # 3. Normalize text
        # ---------------------------------

        claim_words = self._extract_words(
            claim_lower
        )

        evidence_words = self._extract_words(
            evidence_lower
        )

        if not claim_words:
            return "Unsupported"

        # ---------------------------------
        # 4. Remove common cybersecurity
        #    filler words
        # ---------------------------------

        ignored_words = {
            "the",
            "this",
            "that",
            "with",
            "from",
            "which",
            "can",
            "could",
            "would",
            "results",
            "result",
            "information",
            "evidence",
            "source",
            "provides",
            "provided",
            "security"
        }

        claim_words = {
            word
            for word in claim_words
            if word not in ignored_words
        }

        evidence_words = {
            word
            for word in evidence_words
            if word not in ignored_words
        }

        if not claim_words:
            return "Unsupported"

        # ---------------------------------
        # 5. Calculate word overlap
        # ---------------------------------

        matched_words = (
            claim_words & evidence_words
        )

        match_ratio = (
            len(matched_words)
            / len(claim_words)
        )

        # ---------------------------------
        # 6. Strong evidence match
        # ---------------------------------

        if match_ratio >= 0.70:
            return "Supported"

        # ---------------------------------
        # 7. Partial evidence match
        # ---------------------------------

        if match_ratio >= 0.40:
            return "Partially Supported"

        # ---------------------------------
        # 8. Unsupported claim
        # ---------------------------------

        return "Unsupported"

    def _extract_words(self, text):

        words = re.findall(
            r"\b[a-z0-9][a-z0-9._/-]*\b",
            text
        )

        return set(words)