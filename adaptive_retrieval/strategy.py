from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalDecision:
    action: str
    reason: str
    strategy: str
    attempt: int


class AdaptiveRetrievalStrategy:

    def decide(
        self,
        grading: dict[str, Any],
        attempt: int = 1,
        max_attempts: int = 3
    ) -> RetrievalDecision:

        status = grading.get(
            "status",
            "unknown"
        )

        if status == "relevant":
            return RetrievalDecision(
                action="accept",
                reason=(
                    "The retrieved evidence is strongly "
                    "relevant to the investigation."
                ),
                strategy="standard",
                attempt=attempt
            )

        if status == "weak":
            if attempt < max_attempts:
                return RetrievalDecision(
                    action="retry",
                    reason=(
                        "The retrieved evidence is weak. "
                        "Additional retrieval should be "
                        "performed to improve evidence coverage."
                    ),
                    strategy="expanded",
                    attempt=attempt
                )

            return RetrievalDecision(
                action="accept_with_review",
                reason=(
                    "The maximum retrieval attempts were "
                    "reached while evidence remained weak."
                ),
                strategy="expanded",
                attempt=attempt
            )

        if status == "irrelevant":
            if attempt < max_attempts:
                return RetrievalDecision(
                    action="retry",
                    reason=(
                        "The retrieved evidence is irrelevant. "
                        "A broader retrieval strategy should "
                        "be attempted."
                    ),
                    strategy="broad",
                    attempt=attempt
                )

            return RetrievalDecision(
                action="reject",
                reason=(
                    "The maximum retrieval attempts were "
                    "reached without obtaining relevant evidence."
                ),
                strategy="broad",
                attempt=attempt
            )

        if attempt < max_attempts:
            return RetrievalDecision(
                action="retry",
                reason=(
                    "The retrieval quality could not be "
                    "determined reliably. Additional retrieval "
                    "is required."
                ),
                strategy="fallback",
                attempt=attempt
            )

        return RetrievalDecision(
            action="accept_with_review",
            reason=(
                "The maximum retrieval attempts were reached "
                "with an unknown retrieval quality status."
            ),
            strategy="fallback",
            attempt=attempt
        )