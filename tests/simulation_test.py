from simulation.scenario import SimulationScenario
from simulation.simulator import SimulationEngine


def main():
    scenario = SimulationScenario(
        scenario_id="simulation-cve-2026-0544",
        title="CVE-2026-0544 Investigation Scenario",
        description=(
            "Simulate the investigation of a vulnerability "
            "identified through cybersecurity evidence."
        )
    )

    scenario.add_entity(
        entity_id="CVE-2026-0544",
        entity_type="Vulnerability",
        properties={
            "source": "Knowledge Graph"
        }
    )

    scenario.add_assumption(
        "The vulnerability is relevant to the current investigation."
    )

    scenario.add_initial_belief(
        "belief-cve-2026-0544-relevance"
    )

    scenario.set_variable(
        "investigation_mode",
        "vulnerability_analysis"
    )

    engine = SimulationEngine()

    result = engine.run(scenario)

    print("\n" + "=" * 60)
    print("SIMULATION TEST")
    print("=" * 60)

    print(f"Scenario ID: {result.scenario_id}")

    print("\nInitial State:")
    print(result.initial_state)

    print("\nSimulation Events:")
    for event in result.events:
        print(event)

    print("\nSimulation Outcomes:")
    for outcome in result.outcomes:
        print(outcome)

    print("\nFinal State:")
    print(result.final_state)

    print("\nSimulation completed successfully.")


if __name__ == "__main__":
    main()