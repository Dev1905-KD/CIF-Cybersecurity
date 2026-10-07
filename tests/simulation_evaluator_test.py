from simulation.evaluator import SimulationEvaluator


def main():

    hypothesis = {
        "hypothesis_id": "hypothesis-cve-2026-0544-investigation",
        "status": "supported"
    }

    simulation_result = {
        "scenario_id": "simulation-cve-2026-0544",
        "outcomes": [
            {
                "type": "simulation_state_transition",
                "status": "completed"
            }
        ],
        "final_state": {
            "variables": {
                "simulation_completed": True
            }
        }
    }

    evaluator = SimulationEvaluator()

    result = evaluator.evaluate(
        hypothesis=hypothesis,
        simulation_result=simulation_result
    )

    print("\n" + "=" * 60)
    print("SIMULATION HYPOTHESIS EVALUATION TEST")
    print("=" * 60)

    print(
        f"Hypothesis ID: "
        f"{result['hypothesis_id']}"
    )

    print(
        f"Evaluation Status: "
        f"{result['evaluation_status']}"
    )

    print(
        f"Reason: "
        f"{result['reason']}"
    )

    print(
        f"Simulation Scenario: "
        f"{result['simulation_scenario_id']}"
    )

    print(
        f"Outcome Count: "
        f"{result['outcome_count']}"
    )

    print(
        f"Simulation Completed: "
        f"{result['simulation_completed']}"
    )


if __name__ == "__main__":
    main()