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
from world_state.manager import (
    WorldStateManager
)
from belief_graph.manager import BeliefGraphManager
from hypotheses.generator import HypothesisGenerator
from belief_revision.revision import (
    BeliefRevisionEngine
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
        self.world_state = WorldStateManager()
        self.belief_graph = BeliefGraphManager(
            self.world_state
        )
        self.hypothesis_generator = HypothesisGenerator()
        self.belief_revision = BeliefRevisionEngine()
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
        # Update Persistent World State
        # -------------------------

        retrieval_evidence_id = self.world_state.add_evidence({
            "query": query,
            "context": context,
            "retrieval_status": retrieval_result.get("status"),
            "evidence_status": retrieval_result.get("grading", {}).get("status")
        })
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
        # Persist generated answer
        # -------------------------

        self.world_state.add_evidence({
            "type": "generated_answer",
            "query": query,
            "answer": answer
        })
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
        # Update Belief Graph
        # -------------------------

        beliefs = self.belief_graph.update_from_verification(
            query=query,
            answer=answer,
            consensus_result=consensus_result
        )
        
        # -------------------------
        # Generate Hypotheses
        # -------------------------

        hypotheses = self.hypothesis_generator.generate(
            query=query,
            answer=answer,
            consensus_result=consensus_result,
            beliefs=beliefs
        )
        # -------------------------
        # Belief Revision
        # -------------------------

        revision_results = []

        for belief in beliefs:

            revision_result = self.belief_revision.revise(
                belief=belief,
                consensus_status=consensus_result.get("status", "Needs Review"),
                evidence_ids=[retrieval_evidence_id]
            )

            revision_results.append(
                revision_result
            )

            # Sync revised belief with World State
            self.world_state.set_belief(
                belief.belief_id,
                {
                    "belief_id":
                        belief.belief_id,

                    "claim":
                        belief.claim,

                    "status":
                        belief.status,

                    "evidence_ids":
                        belief.evidence_ids,

                    "entity_ids":
                        belief.entity_ids,

                    "verification_status":
                        belief.verification_status,

                    "metadata":
                        belief.metadata,

                    "updated_at":
                        belief.updated_at
                }
            )
        # -------------------------
        # Persist Hypotheses
        # -------------------------

        for hypothesis in hypotheses:
            self.world_state.add_hypothesis({
                "hypothesis_id":
                    hypothesis.hypothesis_id,

                "statement":
                    hypothesis.statement,

                "status":
                    hypothesis.status,

                "entity_ids":
                    hypothesis.entity_ids,

                "belief_ids":
                    hypothesis.belief_ids,

                "verification_status":
                    hypothesis.verification_status,

                "metadata":
                    hypothesis.metadata
            })
        # -------------------------
        # Persist reasoning result
        # -------------------------

        self.world_state.add_verification({
            "query": query,
            "consensus_status": consensus_result.get(
                "status"
            ),
            "evidence_agent": evidence_agent_result.get(
                "status"
            ),
            "graph_agent": graph_agent_result.get(
                "status"
            ),
            "consistency_agent": consistency_agent_result.get(
                "status"
            )
        })

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
            },

            # New Belief Graph
            "beliefs": [
                {
                    "belief_id":
                        belief.belief_id,

                    "claim":
                        belief.claim,

                    "status":
                        belief.status,

                    "entity_ids":
                        belief.entity_ids,

                    "verification_status":
                        belief.verification_status
                }
                for belief in beliefs
            ],
            # New Hypothesis Generation
            "hypotheses": [
                {
                    "hypothesis_id":
                        hypothesis.hypothesis_id,

                    "statement":
                        hypothesis.statement,

                    "status":
                        hypothesis.status,

                    "entity_ids":
                        hypothesis.entity_ids,

                    "belief_ids":
                        hypothesis.belief_ids,

                    "verification_status":
                        hypothesis.verification_status
                }
                for hypothesis in hypotheses
            ],
            "belief_revisions": [
                {
                    "belief_id":
                        revision.belief_id,

                    "previous_status":
                        revision.previous_status,

                    "new_status":
                        revision.new_status,

                    "revision_type":
                        revision.revision_type,

                    "reason":
                        revision.reason,

                    "evidence_ids":
                        revision.evidence_ids,

                    "timestamp":
                        revision.timestamp
                }
                for revision in revision_results
            ]
        }

    def close(self):

        self.crag.close()

        # Graph Agent maintains its own
        # Neo4j connection.
        self.graph_agent.close()

    def get_world_state(self):
        return self.world_state.get_state()