from rag.pipeline import CRAGPipeline
from llm.generator import EvidenceGenerator
from claim_verification.verifier import ClaimVerifier


class CRAGLlamaPipeline:

    def __init__(self):

        self.crag = CRAGPipeline()
        self.generator = EvidenceGenerator()
        self.verifier = ClaimVerifier()

    def run(self, query):

        # -------------------------
        # 1. Corrective Retrieval
        # -------------------------

        retrieval_result = (
            self.crag.run(query)
        )

        if retrieval_result.get(
            "status"
        ) == "error":

            return retrieval_result

        context = retrieval_result.get(
            "context",
            ""
        )

        # -------------------------
        # 2. Check retrieval quality
        # -------------------------

        grading = retrieval_result.get(
            "grading",
            {}
        )

        status = grading.get(
            "status"
        )

        # Map retrieval quality to
        # human-readable evidence status

        evidence_status = {
            "relevant": "Strongly supported",
            "weak": "Partially supported",
            "irrelevant": "Insufficient evidence"
        }

        status_label = evidence_status.get(
            status,
            "Unknown"
        )

        # -------------------------
        # 3. Stop if evidence is insufficient
        # -------------------------

        if status == "irrelevant":

            return {
                "status": "insufficient_evidence",
                "evidence_status": status_label,
                "message":
                    "The available evidence is "
                    "insufficient to answer reliably.",
                "retrieval": retrieval_result
            }

        # -------------------------
        # 4. Llama generation
        # -------------------------

        answer = self.generator.generate(
            query,
            context
        )
        claim_verification = self.verifier.verify_claims(
        answer,
        context
        )

        # -------------------------
        # 5. Final response
        # -------------------------

        return {
            "status": "success",
            "evidence_status": status_label,
            "answer": answer,
            "claim_verification": claim_verification,
            "retrieval": retrieval_result
        }

    def close(self):

        self.crag.close()