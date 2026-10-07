from typing import Any


class SimulationEvaluator:

    def evaluate(
        self,
        hypothesis: dict[str, Any],
        simulation_result: dict[str, Any]
    ) -> dict[str, Any]:

        hypothesis_status = hypothesis.get(
            "status",
            "proposed"
        )

        outcomes = simulation_result.get(
            "outcomes",
            []
        )

        if not outcomes:
            evaluation_status = "needs_review"
            reason = (
                "The simulation produced no outcomes "
                "that can be evaluated."
            )

        elif hypothesis_status == "supported":
            evaluation_status = "supported"
            reason = (
                "The simulation was completed successfully "
                "for a supported hypothesis."
            )

        elif hypothesis_status == "needs_review":
            evaluation_status = "needs_review"
            reason = (
                "The hypothesis requires additional evidence "
                "before simulation results can fully support it."
            )

        elif hypothesis_status == "inconsistent":
            evaluation_status = "contradicted"
            reason = (
                "The hypothesis is inconsistent with the "
                "current verification state."
            )

        else:
            evaluation_status = "proposed"
            reason = (
                "The hypothesis remains proposed because "
                "its evidence is not yet sufficient."
            )

        return {
            "hypothesis_id": hypothesis.get(
                "hypothesis_id"
            ),
            "evaluation_status": evaluation_status,
            "reason": reason,
            "simulation_scenario_id": simulation_result.get(
                "scenario_id"
            ),
            "outcome_count": len(outcomes),
            "simulation_completed": simulation_result.get(
                "final_state",
                {}
            ).get(
                "variables",
                {}
            ).get(
                "simulation_completed",
                False
            )
        }