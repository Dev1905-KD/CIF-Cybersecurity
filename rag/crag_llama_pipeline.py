from rag.pipeline import CRAGPipeline
from llm.generator import EvidenceGenerator
from claim_verification.verifier import ClaimVerifier
from agents.evidence_agent import EvidenceAgent
from agents.graph_agent import GraphAgent
from agents.consistency_agent import ConsistencyAgent
from agents.consensus import ConsensusAgent
from world_state.manager import WorldStateManager
from belief_graph.manager import BeliefGraphManager
from hypotheses.generator import HypothesisGenerator
from belief_revision.revision import BeliefRevisionEngine
from simulation.scenario import SimulationScenario
from simulation.simulator import SimulationEngine
from simulation.evaluator import SimulationEvaluator
from adaptive_retrieval.manager import AdaptiveRetrievalManager
from decision.engine import DecisionEngine


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

        # ---------------------------------
        # Persistent World State
        # ---------------------------------

        self.world_state = WorldStateManager()

        # ---------------------------------
        # Belief Graph
        # ---------------------------------

        self.belief_graph = BeliefGraphManager(
            self.world_state
        )

        # ---------------------------------
        # Hypothesis Generation
        # ---------------------------------

        self.hypothesis_generator = HypothesisGenerator()

        # ---------------------------------
        # Belief Revision
        # ---------------------------------

        self.belief_revision = BeliefRevisionEngine()

        # ---------------------------------
        # Simulation
        # ---------------------------------

        self.simulation_engine = SimulationEngine()
        self.simulation_evaluator = SimulationEvaluator()

        # ---------------------------------
        # Adaptive Retrieval
        # ---------------------------------

        self.adaptive_retrieval = AdaptiveRetrievalManager(
            retriever=self.crag,
            max_attempts=3
        )

        # ---------------------------------
        # Decision Engine
        # ---------------------------------

        self.decision_engine = DecisionEngine()

    def run(self, query):

        # ---------------------------------
        # 1. Adaptive Corrective Retrieval
        # ---------------------------------

        adaptive_retrieval_result = (
            self.adaptive_retrieval.retrieve(query)
        )

        retrieval_result = (
            adaptive_retrieval_result.get(
                "retrieval_result",
                {}
            )
        )

        if retrieval_result.get("status") == "error":
            return {
                "status": "error",
                "message": retrieval_result.get(
                    "message",
                    "Adaptive retrieval failed."
                ),
                "adaptive_retrieval": (
                    adaptive_retrieval_result
                )
            }

        context = retrieval_result.get(
            "context",
            ""
        )

        # ---------------------------------
        # Persist Adaptive Retrieval State
        # ---------------------------------

        self.world_state.add_verification(
            {
                "type": "adaptive_retrieval",
                "query": query,
                "attempts": (
                    adaptive_retrieval_result.get(
                        "attempts",
                        []
                    )
                ),
                "final_decision": (
                    adaptive_retrieval_result.get(
                        "final_decision",
                        {}
                    )
                ),
                "final_grading": (
                    retrieval_result.get(
                        "grading",
                        {}
                    )
                )
            }
        )

        # ---------------------------------
        # Update Persistent World State
        # ---------------------------------

        retrieval_evidence_id = (
            self.world_state.add_evidence(
                {
                    "query": query,
                    "context": context,
                    "retrieval_status": (
                        retrieval_result.get(
                            "status"
                        )
                    ),
                    "evidence_status": (
                        retrieval_result.get(
                            "grading",
                            {}
                        ).get(
                            "status"
                        )
                    ),
                    "adaptive_retrieval": (
                        adaptive_retrieval_result
                    )
                }
            )
        )

        # ---------------------------------
        # 2. Check Retrieval Quality
        # ---------------------------------

        grading = retrieval_result.get(
            "grading",
            {}
        )

        status = grading.get(
            "status"
        )

        evidence_status = {
            "relevant": "Strongly supported",
            "weak": "Partially supported",
            "irrelevant": "Insufficient evidence"
        }

        status_label = evidence_status.get(
            status,
            "Unknown"
        )

        # ---------------------------------
        # 3. Stop if Evidence is Insufficient
        # ---------------------------------

        final_retrieval_decision = (
            adaptive_retrieval_result.get(
                "final_decision",
                {}
            )
        )

        if (
            status == "irrelevant"
            or final_retrieval_decision.get(
                "action"
            ) == "reject"
        ):
            return {
                "status": "insufficient_evidence",
                "evidence_status": status_label,
                "message": (
                    "The available evidence is "
                    "insufficient to answer reliably "
                    "after adaptive retrieval."
                ),
                "retrieval": retrieval_result,
                "adaptive_retrieval": (
                    adaptive_retrieval_result
                )
            }

        # ---------------------------------
        # 4. Llama Generation
        # ---------------------------------

        answer = self.generator.generate(
            query,
            context
        )

        # ---------------------------------
        # Persist Generated Answer
        # ---------------------------------

        self.world_state.add_evidence(
            {
                "type": "generated_answer",
                "query": query,
                "answer": answer
            }
        )

        # ---------------------------------
        # 5. Existing Claim Verification
        # ---------------------------------

        claim_verification = (
            self.verifier.verify_claims(
                answer,
                context
            )
        )

        # ---------------------------------
        # 6. Evidence Agent
        # ---------------------------------

        evidence_agent_result = (
            self.evidence_agent.verify(
                answer,
                context
            )
        )

        # ---------------------------------
        # 7. Graph Agent
        # ---------------------------------

        graph_agent_result = (
            self.graph_agent.verify(
                answer
            )
        )

        # ---------------------------------
        # 8. Consistency Agent
        # ---------------------------------

        consistency_agent_result = (
            self.consistency_agent.verify(
                answer,
                context
            )
        )

        # ---------------------------------
        # 9. Consensus Agent
        # ---------------------------------

        consensus_result = (
            self.consensus_agent.evaluate(
                evidence_agent_result,
                graph_agent_result,
                consistency_agent_result
            )
        )

        # ---------------------------------
        # Update Belief Graph
        # ---------------------------------

        beliefs = (
            self.belief_graph.update_from_verification(
                query=query,
                answer=answer,
                consensus_result=consensus_result
            )
        )

        # ---------------------------------
        # Generate Hypotheses
        # ---------------------------------

        hypotheses = (
            self.hypothesis_generator.generate(
                query=query,
                answer=answer,
                consensus_result=consensus_result,
                beliefs=beliefs
            )
        )

        # ---------------------------------
        # Initial Belief Revision
        # ---------------------------------

        revision_results = []

        for belief in beliefs:

            revision_result = (
                self.belief_revision.revise(
                    belief=belief,
                    consensus_status=(
                        consensus_result.get(
                            "status",
                            "Needs Review"
                        )
                    ),
                    evidence_ids=[
                        retrieval_evidence_id
                    ]
                )
            )

            revision_results.append(
                revision_result
            )

            self.world_state.set_belief(
                belief.belief_id,
                {
                    "belief_id": belief.belief_id,
                    "claim": belief.claim,
                    "status": belief.status,
                    "evidence_ids": (
                        belief.evidence_ids
                    ),
                    "entity_ids": (
                        belief.entity_ids
                    ),
                    "verification_status": (
                        belief.verification_status
                    ),
                    "metadata": belief.metadata,
                    "updated_at": belief.updated_at
                }
            )

        # ---------------------------------
        # Build Simulation Scenario
        # ---------------------------------

        simulation_scenario = SimulationScenario(
            scenario_id=(
                f"simulation-"
                f"{query[:30].lower().replace(' ', '-')}"
            ),
            title="Cybersecurity Investigation Simulation",
            description=query,
            initial_beliefs=[
                belief.belief_id
                for belief in beliefs
            ]
        )

        for belief in beliefs:

            for entity_id in belief.entity_ids:

                simulation_scenario.add_entity(
                    entity_id=entity_id,
                    entity_type="InvestigationEntity",
                    properties={
                        "belief_id": belief.belief_id,
                        "belief_status": belief.status
                    }
                )

        simulation_scenario.set_variable(
            "consensus_status",
            consensus_result.get(
                "status",
                "Needs Review"
            )
        )

        # ---------------------------------
        # Run Simulation
        # ---------------------------------

        simulation_result = (
            self.simulation_engine.run(
                simulation_scenario
            )
        )

        simulation_dict = (
            simulation_result.to_dict()
        )

        self.world_state.add_simulation(
            simulation_dict
        )

        # ---------------------------------
        # Persist Hypotheses
        # ---------------------------------

        for hypothesis in hypotheses:

            self.world_state.add_hypothesis(
                {
                    "hypothesis_id": (
                        hypothesis.hypothesis_id
                    ),
                    "statement": (
                        hypothesis.statement
                    ),
                    "status": hypothesis.status,
                    "entity_ids": (
                        hypothesis.entity_ids
                    ),
                    "belief_ids": (
                        hypothesis.belief_ids
                    ),
                    "verification_status": (
                        hypothesis.verification_status
                    ),
                    "metadata": hypothesis.metadata
                }
            )

        # ---------------------------------
        # Evaluate Hypotheses Against Simulation
        # ---------------------------------

        hypothesis_evaluations = []

        for hypothesis in hypotheses:

            evaluation = (
                self.simulation_evaluator.evaluate(
                    hypothesis={
                        "hypothesis_id": (
                            hypothesis.hypothesis_id
                        ),
                        "status": hypothesis.status
                    },
                    simulation_result=simulation_dict
                )
            )

            hypothesis_evaluations.append(
                evaluation
            )

        # ---------------------------------
        # Simulation-Driven Belief Revision
        # ---------------------------------

        simulation_belief_revisions = []

        for evaluation in hypothesis_evaluations:

            hypothesis_id = evaluation.get(
                "hypothesis_id"
            )

            matching_hypothesis = next(
                (
                    hypothesis
                    for hypothesis in hypotheses
                    if hypothesis.hypothesis_id
                    == hypothesis_id
                ),
                None
            )

            if matching_hypothesis is None:
                continue

            for belief in beliefs:

                if (
                    belief.belief_id
                    not in matching_hypothesis.belief_ids
                ):
                    continue

                simulation_revision = (
                    self.belief_revision.revise_from_simulation(
                        belief=belief,
                        hypothesis_evaluation=evaluation,
                        evidence_ids=[
                            retrieval_evidence_id
                        ]
                    )
                )

                simulation_belief_revisions.append(
                    simulation_revision
                )

                self.world_state.set_belief(
                    belief.belief_id,
                    {
                        "belief_id": belief.belief_id,
                        "claim": belief.claim,
                        "status": belief.status,
                        "evidence_ids": (
                            belief.evidence_ids
                        ),
                        "entity_ids": (
                            belief.entity_ids
                        ),
                        "verification_status": (
                            belief.verification_status
                        ),
                        "metadata": belief.metadata,
                        "updated_at": belief.updated_at
                    }
                )

                self.world_state.add_verification(
                    {
                        "type": (
                            "simulation_belief_revision"
                        ),
                        "belief_id": (
                            belief.belief_id
                        ),
                        "hypothesis_id": (
                            hypothesis_id
                        ),
                        "evaluation_status": (
                            evaluation.get(
                                "evaluation_status"
                            )
                        ),
                        "new_status": (
                            simulation_revision.new_status
                        ),
                        "revision_type": (
                            simulation_revision.revision_type
                        ),
                        "reason": (
                            simulation_revision.reason
                        )
                    }
                )

        # ---------------------------------
        # Persist Final Reasoning Result
        # ---------------------------------

        self.world_state.add_verification(
            {
                "query": query,
                "consensus_status": (
                    consensus_result.get(
                        "status"
                    )
                ),
                "evidence_agent": (
                    evidence_agent_result.get(
                        "status"
                    )
                ),
                "graph_agent": (
                    graph_agent_result.get(
                        "status"
                    )
                ),
                "consistency_agent": (
                    consistency_agent_result.get(
                        "status"
                    )
                )
            }
        )

        # ---------------------------------
        # Build Pipeline State
        # ---------------------------------

        pipeline_state = {
            "status": "success",
            "evidence_status": status_label,
            "answer": answer,

            "adaptive_retrieval": (
                adaptive_retrieval_result
            ),

            "claim_verification": (
                claim_verification
            ),

            "retrieval": retrieval_result,

            "multi_agent_verification": {
                "evidence_agent": (
                    evidence_agent_result
                ),
                "graph_agent": (
                    graph_agent_result
                ),
                "consistency_agent": (
                    consistency_agent_result
                ),
                "consensus": (
                    consensus_result
                )
            },

            "beliefs": [
                {
                    "belief_id": belief.belief_id,
                    "claim": belief.claim,
                    "status": belief.status,
                    "entity_ids": belief.entity_ids,
                    "verification_status": (
                        belief.verification_status
                    )
                }
                for belief in beliefs
            ],

            "hypotheses": [
                {
                    "hypothesis_id": (
                        hypothesis.hypothesis_id
                    ),
                    "statement": (
                        hypothesis.statement
                    ),
                    "status": hypothesis.status,
                    "entity_ids": (
                        hypothesis.entity_ids
                    ),
                    "belief_ids": (
                        hypothesis.belief_ids
                    ),
                    "verification_status": (
                        hypothesis.verification_status
                    )
                }
                for hypothesis in hypotheses
            ],

            "belief_revisions": [
                {
                    "belief_id": revision.belief_id,
                    "previous_status": (
                        revision.previous_status
                    ),
                    "new_status": (
                        revision.new_status
                    ),
                    "revision_type": (
                        revision.revision_type
                    ),
                    "reason": revision.reason,
                    "evidence_ids": (
                        revision.evidence_ids
                    ),
                    "timestamp": revision.timestamp
                }
                for revision in revision_results
            ],

            "simulation": simulation_dict,

            "hypothesis_evaluations": (
                hypothesis_evaluations
            ),

            "simulation_belief_revisions": [
                {
                    "belief_id": revision.belief_id,
                    "previous_status": (
                        revision.previous_status
                    ),
                    "new_status": (
                        revision.new_status
                    ),
                    "revision_type": (
                        revision.revision_type
                    ),
                    "reason": revision.reason,
                    "evidence_ids": (
                        revision.evidence_ids
                    ),
                    "timestamp": revision.timestamp
                }
                for revision in simulation_belief_revisions
            ]
        }

        # ---------------------------------
        # Decision Engine
        # ---------------------------------

        decision = self.decision_engine.decide(
            query=query,
            pipeline_result=pipeline_state
        )

        decision_result = decision.to_dict()

        # ---------------------------------
        # Persist Decision
        # ---------------------------------

        self.world_state.add_verification(
            {
                "type": "decision",
                "query": query,
                "decision": decision_result
            }
        )

        # ---------------------------------
        # Add Decision to Final Pipeline State
        # ---------------------------------

        pipeline_state["decision"] = decision_result

        return pipeline_state

    def close(self):

        self.crag.close()

        # Graph Agent maintains its own
        # Neo4j connection.
        self.graph_agent.close()

    def get_world_state(self):

        return self.world_state.get_state()