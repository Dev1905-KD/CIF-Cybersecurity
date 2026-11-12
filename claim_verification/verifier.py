
import re


class ClaimVerifier:

    IGNORED_WORDS = {
        "the", "this", "that", "with", "from", "which",
        "can", "could", "would", "should", "their",
        "there", "these", "those", "about", "based",
        "using", "used", "uses", "also", "into",
        "such", "than", "then", "when", "where",
        "what", "while", "because", "provides",
        "provided", "information", "evidence",
        "finding", "reasoning", "supporting",
        "limitations", "source", "claim"
    }

    HEADINGS = {
        "finding",
        "supporting evidence",
        "reasoning",
        "limitations"
    }

    def verify_claims(self, answer, evidence):

        results = []

        evidence_lower = (evidence or "").lower()

        for line in answer.splitlines():

            claim = self._clean_line(line)

            if not claim:
                continue

            if self._is_heading(claim):
                continue

            # Verify individual sentences instead of combining
            # multiple statements into one claim.
            sentences = re.split(
                r"(?<=[.!?])\s+",
                claim
            )

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                if self._is_non_verifiable_boilerplate(sentence):
                    continue

                status = self._verify_claim(
                    sentence,
                    evidence_lower
                )

                results.append({
                    "claim": sentence,
                    "status": status
                })

        return results

    # ---------------------------------
    # Markdown and line cleaning
    # ---------------------------------

    def _clean_line(self, line):

        line = line.strip()

        line = re.sub(
            r"^\s*#{1,6}\s*",
            "",
            line
        )

        line = re.sub(
            r"^\s*(?:[-*•]+|\d+[.)])\s*",
            "",
            line
        )

        line = line.replace("**", "")
        line = line.replace("__", "")
        line = line.replace("`", "")

        return line.strip()

    # ---------------------------------
    # Heading detection
    # ---------------------------------

    def _is_heading(self, claim):

        normalized = claim.lower().strip(
            " .:#*-_"
        )

        return (
            normalized in self.HEADINGS
            or claim.endswith(":")
        )

    # ---------------------------------
    # Non-verifiable assessment statements
    # ---------------------------------

    def _is_non_verifiable_boilerplate(self, claim):

        normalized = re.sub(
            r"[^a-z ]",
            "",
            claim.lower()
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized
        ).strip()

        ignored_statements = {
            "no additional limitations were identified in the retrieved context",
            "no additional limitations were identified",
            "no material limitations were identified in the retrieved context",
            "no material limitations identified in the retrieved evidence",
            "no material limitations identified in the retrieved context"
        }

        if normalized in ignored_statements:
            return True

        assessment_patterns = [
            r"^the vulnerability finding is supported by the retrieved evidence",
            r"^the finding is supported by the retrieved evidence",
            r"^the evidence clearly outlines the attack conditions",

            # Evidence-assessment statements are not independent
            # cybersecurity facts.
            r"^the retrieved evidence directly supports the finding",
            r"^the retrieved evidence supports the finding",
            r"^the finding aligns with the retrieved evidence"
        ]

        for pattern in assessment_patterns:

            if re.search(pattern, normalized):
                return True

        return False

    # ---------------------------------
    # Claim verification
    # ---------------------------------

    def _verify_claim(self, claim, evidence_lower):

        claim_lower = claim.lower().strip()

        if not claim_lower:
            return "Unsupported"

        if claim_lower in evidence_lower:
            return "Supported"

        claim_words = self._extract_words(
            claim_lower
        )

        evidence_words = self._extract_words(
            evidence_lower
        )

        claim_words -= self.IGNORED_WORDS
        evidence_words -= self.IGNORED_WORDS

        if not claim_words:
            return "Unsupported"

        anchors = self._extract_anchors(
            claim_lower
        )

        missing_anchors = [
            anchor
            for anchor in anchors
            if anchor.lower() not in evidence_lower
        ]

        if missing_anchors:
            return "Unsupported"

        matched_words = (
            claim_words & evidence_words
        )

        match_ratio = (
            len(matched_words) / len(claim_words)
        )

        if anchors and match_ratio >= 0.70:
            return "Supported"

        if not anchors and match_ratio >= 0.80:
            return "Supported"

        if match_ratio >= 0.40:
            return "Partially Supported"

        return "Unsupported"

    # ---------------------------------
    # Word extraction
    # ---------------------------------

    def _extract_words(self, text):

        return set(
            re.findall(
                r"\b[a-z0-9][a-z0-9._/-]*\b",
                text
            )
        )

    # ---------------------------------
    # Anchor extraction
    # ---------------------------------

    def _extract_anchors(self, text):

        patterns = [
            r"\bCVE-\d{4}-\d{4,7}\b",
            r"\bT\d{4}(?:\.\d{3})?\b",
            r"\b(?:sha256|sha1|md5)\b",
            r"\b[a-f0-9]{32,64}\b",
            r"\b\d+(?:\.\d+)+\b",
            r"\b\d+(?:\.\d+)?%\b"
        ]

        anchors = []

        for pattern in patterns:

            anchors.extend(
                re.findall(
                    pattern,
                    text,
                    re.IGNORECASE
                )
            )

        return list(
            dict.fromkeys(anchors)
        )
