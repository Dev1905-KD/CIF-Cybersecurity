from dataclasses import asdict
from typing import Any

from adaptive_retrieval.strategy import (
    AdaptiveRetrievalStrategy,
    RetrievalDecision
)


class AdaptiveRetrievalManager:

    def __init__(
        self,
        retriever,
        max_attempts: int = 3
    ):
        self.retriever = retriever
        self.max_attempts = max_attempts
        self.strategy = AdaptiveRetrievalStrategy()

    def retrieve(self, query: str) -> dict[str, Any]:
        attempts = []
        current_query = query
        final_result = None
        final_decision = None

        for attempt_number in range(
            1,
            self.max_attempts + 1
        ):
            try:
                retrieval_result = self.retriever.run(
                    current_query
                )
            except Exception as exc:
                retrieval_result = {
                    "status": "error",
                    "message": str(exc),
                    "context": "",
                    "grading": {
                        "status": "unknown"
                    }
                }

            grading = retrieval_result.get(
                "grading",
                {}
            )

            decision = self.strategy.decide(
                grading=grading,
                attempt=attempt_number,
                max_attempts=self.max_attempts
            )

            attempt_record = {
                "attempt": attempt_number,
                "query": current_query,
                "retrieval_status": retrieval_result.get(
                    "status"
                ),
                "grading_status": grading.get(
                    "status",
                    "unknown"
                ),
                "grading": grading,
                "decision": decision.action,
                "strategy": decision.strategy,
                "reason": decision.reason
            }

            attempts.append(attempt_record)

            final_result = retrieval_result
            final_decision = decision

            if retrieval_result.get("status") == "error":
                break

            if decision.action in {
                "accept",
                "accept_with_review",
                "reject"
            }:
                break

            current_query = self._build_retry_query(
                query=query,
                strategy=decision.strategy,
                attempt=attempt_number
            )

        if final_result is None:
            final_result = {
                "status": "error",
                "message": (
                    "Adaptive retrieval produced no result."
                ),
                "context": "",
                "grading": {
                    "status": "unknown"
                }
            }

        if final_decision is None:
            final_decision = RetrievalDecision(
                action="reject",
                reason=(
                    "Adaptive retrieval could not produce "
                    "a retrieval decision."
                ),
                strategy="fallback",
                attempt=0
            )

        return {
            "status": final_result.get(
                "status",
                "error"
            ),
            "context": final_result.get(
                "context",
                ""
            ),
            "grading": final_result.get(
                "grading",
                {}
            ),
            "retrieval_result": final_result,
            "attempts": attempts,
            "final_decision": asdict(
                final_decision
            )
        }

    def _build_retry_query(
        self,
        query: str,
        strategy: str,
        attempt: int
    ) -> str:

        if strategy == "expanded":
            return (
                f"{query} "
                "technical details affected products "
                "vulnerability details exploit information"
            )

        if strategy == "broad":
            return (
                f"{query} "
                "related products vendors vulnerabilities "
                "security impact references"
            )

        if strategy == "fallback":
            return (
                f"{query} "
                "cybersecurity vulnerability information "
                "CVE evidence affected products"
            )

        return query