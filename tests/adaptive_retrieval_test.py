from adaptive_retrieval.manager import (
    AdaptiveRetrievalManager
)


class FakeRetriever:

    def __init__(self, results):
        self.results = results
        self.index = 0

    def run(self, query):
        result = self.results[
            min(
                self.index,
                len(self.results) - 1
            )
        ]

        self.index += 1
        return result


def test_relevant_evidence_is_accepted():
    retriever = FakeRetriever(
        [
            {
                "status": "success",
                "context": "Strong evidence",
                "grading": {
                    "status": "relevant"
                }
            }
        ]
    )

    manager = AdaptiveRetrievalManager(
        retriever,
        max_attempts=3
    )

    result = manager.retrieve(
        "What is CVE-2026-0544?"
    )

    assert result["final_decision"]["action"] == "accept"
    assert len(result["attempts"]) == 1


def test_weak_evidence_triggers_retry():
    retriever = FakeRetriever(
        [
            {
                "status": "success",
                "context": "Weak evidence",
                "grading": {
                    "status": "weak"
                }
            },
            {
                "status": "success",
                "context": "Strong evidence",
                "grading": {
                    "status": "relevant"
                }
            }
        ]
    )

    manager = AdaptiveRetrievalManager(
        retriever,
        max_attempts=3
    )

    result = manager.retrieve(
        "What is CVE-2026-0544?"
    )

    assert len(result["attempts"]) == 2
    assert result["attempts"][0]["decision"] == "retry"
    assert result["attempts"][0]["strategy"] == "expanded"
    assert result["final_decision"]["action"] == "accept"


def test_irrelevant_evidence_triggers_broad_retry():
    retriever = FakeRetriever(
        [
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "irrelevant"
                }
            },
            {
                "status": "success",
                "context": "Relevant evidence",
                "grading": {
                    "status": "relevant"
                }
            }
        ]
    )

    manager = AdaptiveRetrievalManager(
        retriever,
        max_attempts=3
    )

    result = manager.retrieve(
        "What is CVE-2026-0544?"
    )

    assert len(result["attempts"]) == 2
    assert result["attempts"][0]["decision"] == "retry"
    assert result["attempts"][0]["strategy"] == "broad"
    assert result["final_decision"]["action"] == "accept"


def test_unknown_status_uses_fallback():
    retriever = FakeRetriever(
        [
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "unknown"
                }
            },
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "unknown"
                }
            },
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "unknown"
                }
            }
        ]
    )

    manager = AdaptiveRetrievalManager(
        retriever,
        max_attempts=3
    )

    result = manager.retrieve(
        "Unknown cybersecurity question"
    )

    assert len(result["attempts"]) == 3
    assert (
        result["final_decision"]["action"]
        == "accept_with_review"
    )
    assert (
        result["final_decision"]["strategy"]
        == "fallback"
    )


def test_max_attempts_rejects_irrelevant_evidence():
    retriever = FakeRetriever(
        [
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "irrelevant"
                }
            },
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "irrelevant"
                }
            },
            {
                "status": "success",
                "context": "",
                "grading": {
                    "status": "irrelevant"
                }
            }
        ]
    )

    manager = AdaptiveRetrievalManager(
        retriever,
        max_attempts=3
    )

    result = manager.retrieve(
        "Unrelated cybersecurity question"
    )

    assert len(result["attempts"]) == 3
    assert result["final_decision"]["action"] == "reject"


def main():
    test_relevant_evidence_is_accepted()
    test_weak_evidence_triggers_retry()
    test_irrelevant_evidence_triggers_broad_retry()
    test_unknown_status_uses_fallback()
    test_max_attempts_rejects_irrelevant_evidence()

    print("=" * 60)
    print("ADAPTIVE RETRIEVAL TEST")
    print("=" * 60)
    print("Relevant evidence: PASS")
    print("Weak evidence retry: PASS")
    print("Irrelevant evidence broad retry: PASS")
    print("Unknown evidence fallback: PASS")
    print("Maximum attempts rejection: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()