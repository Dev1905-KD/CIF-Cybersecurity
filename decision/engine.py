from typing import Any

from decision.decision import Decision


class DecisionEngine:
    """
    Converts the verified state of the CIF reasoning cycle
    into a structured cybersecurity decision.

    The engine does not invent evidence or numerical confidence.
    Decisions are based only on the outputs already produced by
    retrieval, multi-agent verification, hypotheses, and simulation.
    """

    def decide(
        self,
        query: str,
        pipeline_result: dict[str, Any],
    ) -> Decision:
        consensus = (
            pipeline_result
            .get("multi_agent_verification", {})
            .get("consensus", {})
        )

        verification_status = consensus.get(
            "status",
            "Unknown"
        )

        hypotheses = pipeline_result.get(
            "hypotheses",
            []
        )

        hypothesis_evaluations = pipeline_result.get(
            "hypothesis_evaluations",
            []
        )

        adaptive_retrieval = pipeline_result.get(
            "adaptive_retrieval",
            {}
        )

        retrieval_decision = adaptive_retrieval.get(
            "final_decision",
            {}
        )

        retrieval_action = retrieval_decision.get(
            "action",
            "unknown"
        )

        simulation_status = self._simulation_status(
            pipeline_result
        )

        hypothesis_status = self._hypothesis_status(
            hypotheses,
            hypothesis_evaluations
        )

        decision_status = "review"
        risk_level = "medium"

        recommended_actions: list[str] = []
        supporting_evidence: list[str] = []

        if verification_status == "Verified":
            supporting_evidence.append(
                "Multi-agent verification reached Verified status."
            )

        elif verification_status == "Needs Review":
            supporting_evidence.append(
                "Multi-agent verification requires additional review."
            )

        elif verification_status == "Inconsistent":
            supporting_evidence.append(
                "Multi-agent verification detected an inconsistency."
            )

        if hypothesis_status == "supported":
            supporting_evidence.append(
                "At least one hypothesis is supported."
            )

        elif hypothesis_status == "needs_review":
            supporting_evidence.append(
                "The generated hypothesis requires additional evidence."
            )

        if simulation_status == "supported":
            supporting_evidence.append(
                "Simulation evaluation supports the current hypothesis."
            )

        elif simulation_status == "needs_review":
            supporting_evidence.append(
                "Simulation evaluation requires further review."
            )

        elif simulation_status == "contradicted":
            supporting_evidence.append(
                "Simulation evaluation contradicts the current hypothesis."
            )

        if retrieval_action == "reject":
            decision_status = "insufficient_evidence"
            risk_level = "unknown"

            recommended_actions = [
                "Perform additional evidence retrieval.",
                "Do not rely on the current answer for a final security decision.",
            ]

            rationale = (
                "Adaptive retrieval rejected the available evidence "
                "after exhausting the configured retrieval attempts."
            )

        elif verification_status == "Inconsistent":
            decision_status = "block"
            risk_level = "high"

            recommended_actions = [
                "Investigate the conflicting evidence.",
                "Re-run verification after resolving the inconsistency.",
                "Do not treat the current hypothesis as confirmed.",
            ]

            rationale = (
                "The verification layer detected inconsistent evidence "
                "or relationships, so the current reasoning state should "
                "not be used for an operational decision."
            )

        elif (
            verification_status == "Verified"
            and hypothesis_status == "supported"
            and simulation_status == "supported"
        ):
            decision_status = "proceed"
            risk_level = "high"

            recommended_actions = [
                "Proceed with the cybersecurity investigation.",
                "Validate the identified vulnerability and affected assets.",
                "Use the verified evidence as the basis for the next investigation step.",
            ]

            rationale = (
                "The evidence was verified by the multi-agent verification "
                "layer, the hypothesis is supported, and simulation evaluation "
                "supports the resulting reasoning state."
            )

        elif verification_status == "Verified":
            decision_status = "review"
            risk_level = "medium"

            recommended_actions = [
                "Review the hypothesis and simulation results.",
                "Retrieve additional evidence if operational confirmation is required.",
            ]

            rationale = (
                "The available evidence passed multi-agent verification, "
                "but the hypothesis or simulation stage does not provide "
                "sufficient support for a fully confirmed decision."
            )

        else:
            decision_status = "review"
            risk_level = "medium"

            recommended_actions = [
                "Review the current evidence and belief state.",
                "Retrieve additional evidence before taking an operational action.",
            ]

            rationale = (
                "The current reasoning cycle does not provide sufficient "
                "verification and hypothesis support for a confirmed decision."
            )

        return Decision(
            decision_id=self._build_decision_id(query),
            status=decision_status,
            risk_level=risk_level,
            rationale=rationale,
            recommended_actions=recommended_actions,
            supporting_evidence=supporting_evidence,
            verification_status=verification_status,
            hypothesis_status=hypothesis_status,
            simulation_status=simulation_status,
            metadata={
                "retrieval_action": retrieval_action,
                "hypothesis_count": len(hypotheses),
                "hypothesis_evaluation_count": len(
                    hypothesis_evaluations
                ),
            },
        )

    def _hypothesis_status(
        self,
        hypotheses: list[dict[str, Any]],
        evaluations: list[dict[str, Any]],
    ) -> str:
        evaluation_statuses = {
            evaluation.get("evaluation_status")
            for evaluation in evaluations
        }

        if "contradicted" in evaluation_statuses:
            return "contradicted"

        if "supported" in evaluation_statuses:
            return "supported"

        if "needs_review" in evaluation_statuses:
            return "needs_review"

        hypothesis_statuses = {
            hypothesis.get("status")
            for hypothesis in hypotheses
        }

        if "supported" in hypothesis_statuses:
            return "supported"

        if "inconsistent" in hypothesis_statuses:
            return "contradicted"

        if "needs_review" in hypothesis_statuses:
            return "needs_review"

        if hypotheses:
            return "proposed"

        return "unknown"

    def _simulation_status(
        self,
        pipeline_result: dict[str, Any],
    ) -> str:
        evaluations = pipeline_result.get(
            "hypothesis_evaluations",
            []
        )

        statuses = {
            evaluation.get("evaluation_status")
            for evaluation in evaluations
        }

        if "contradicted" in statuses:
            return "contradicted"

        if "supported" in statuses:
            return "supported"

        if "needs_review" in statuses:
            return "needs_review"

        if "proposed" in statuses:
            return "proposed"

        simulation = pipeline_result.get(
            "simulation",
            {}
        )

        completed = (
            simulation
            .get("final_state", {})
            .get("variables", {})
            .get("simulation_completed", False)
        )

        if completed:
            return "completed"

        return "unknown"

    def _build_decision_id(self, query: str) -> str:
        normalized = (
            query.strip()
            .lower()
            .replace(" ", "-")
        )

        normalized = "".join(
            character
            for character in normalized
            if character.isalnum() or character == "-"
        )

        return f"decision-{normalized[:50]}"