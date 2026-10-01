from rag.pipeline import CRAGPipeline
from llm.generator import EvidenceGenerator
from claim_verification.verifier import ClaimVerifier

from agents.evidence_agent import (
    EvidenceAgent
)

from agents.graph_agent import (
    GraphAgent
)

from agents.consistency_agent import (
    ConsistencyAgent
)

from agents.consensus import (
    ConsensusAgent
)


class CRAGLlamaPipeline:

    def __init__(self):

        self.crag = CRAGPipeline()
        self.generator = EvidenceGenerator()
        self.verifier = ClaimVerifier()

        # ---------------------------------
        # Multi-Agent Verification
        # ---------------------------------

        self.evidence_agent = EvidenceAgent()
        self.graph_agent = GraphAgent()
        self.consistency_agent = ConsistencyAgent()
        self.consensus_agent = ConsensusAgent()

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

        # -------------------------
        # 5. Existing claim verification
        # -------------------------

        claim_verification = (
            self.verifier.verify_claims(
                answer,
                context
            )
        )

        # -------------------------
        # 6. Evidence Agent
        # -------------------------

        evidence_agent_result = (
            self.evidence_agent.verify(
                answer,
                context
            )
        )

        # -------------------------
        # 7. Graph Agent
        # -------------------------

        graph_agent_result = (
            self.graph_agent.verify(
                answer
            )
        )

        # -------------------------
        # 8. Consistency Agent
        # -------------------------

        consistency_agent_result = (
            self.consistency_agent.verify(
                answer,
                context
            )
        )

        # -------------------------
        # 9. Consensus Agent
        # -------------------------

        consensus_result = (
            self.consensus_agent.evaluate(
                evidence_agent_result,
                graph_agent_result,
                consistency_agent_result
            )
        )

        # -------------------------
        # 10. Final response
        # -------------------------

        return {
            "status": "success",
            "evidence_status": status_label,
            "answer": answer,

            # Existing verification
            "claim_verification":
                claim_verification,

            # Existing retrieval
            "retrieval":
                retrieval_result,

            # New multi-agent verification
            "multi_agent_verification": {

                "evidence_agent":
                    evidence_agent_result,

                "graph_agent":
                    graph_agent_result,

                "consistency_agent":
                    consistency_agent_result,

                "consensus":
                    consensus_result
            }
        }

    def close(self):

        self.crag.close()

        # Graph Agent maintains its own
        # Neo4j connection.
        self.graph_agent.close()