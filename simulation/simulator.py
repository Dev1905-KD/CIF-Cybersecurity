from datetime import datetime
from typing import Any

from simulation.scenario import (
    SimulationScenario,
    SimulationEvent,
    SimulationOutcome
)


class SimulationResult:
    def __init__(
        self,
        scenario_id: str,
        initial_state: dict[str, Any],
        final_state: dict[str, Any],
        events: list[dict[str, Any]],
        outcomes: list[dict[str, Any]]
    ):
        self.scenario_id = scenario_id
        self.initial_state = initial_state
        self.final_state = final_state
        self.events = events
        self.outcomes = outcomes
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "initial_state": self.initial_state,
            "final_state": self.final_state,
            "events": self.events,
            "outcomes": self.outcomes,
            "created_at": self.created_at
        }


class SimulationEngine:
    def run(
        self,
        scenario: SimulationScenario
    ) -> SimulationResult:

        initial_state = {
            "entities": list(scenario.entities),
            "beliefs": list(scenario.initial_beliefs),
            "variables": dict(scenario.variables)
        }

        current_state = {
            "entities": list(scenario.entities),
            "beliefs": list(scenario.initial_beliefs),
            "variables": dict(scenario.variables)
        }

        events = []
        outcomes = []

        for entity in scenario.entities:

            event = SimulationEvent(
                event_type="entity_observation",
                description=(
                    f"Observed entity {entity['id']} "
                    f"of type {entity['type']}."
                ),
                entity_ids=[
                    entity["id"]
                ]
            )

            events.append({
                "type": event.event_type,
                "description": event.description,
                "entity_ids": event.entity_ids,
                "metadata": event.metadata,
                "timestamp": event.timestamp
            })

        for assumption in scenario.assumptions:

            outcome = SimulationOutcome(
                outcome_id=f"assumption-{len(outcomes) + 1}",
                status="considered",
                description=assumption
            )

            outcomes.append({
                "type": "assumption_evaluation",
                "outcome_id": outcome.outcome_id,
                "status": outcome.status,
                "description": outcome.description,
                "affected_beliefs": outcome.affected_beliefs,
                "affected_entities": outcome.affected_entities,
                "metadata": outcome.metadata
            })

        if scenario.initial_beliefs:

            current_state["variables"][
                "beliefs_under_simulation"
            ] = list(
                scenario.initial_beliefs
            )

            events.append({
                "type": "belief_state_observation",
                "beliefs": list(
                    scenario.initial_beliefs
                ),
                "timestamp": datetime.utcnow().isoformat()
            })

        current_state["variables"][
            "simulation_completed"
        ] = True

        current_state["variables"][
            "state_transition_count"
        ] = len(events)

        outcomes.append({
            "type": "simulation_state_transition",
            "initial_belief_count": len(
                scenario.initial_beliefs
            ),
            "final_belief_count": len(
                current_state.get("beliefs", [])
            ),
            "events_generated": len(events),
            "status": "completed"
        })

        return SimulationResult(
            scenario_id=scenario.scenario_id,
            initial_state=initial_state,
            final_state=current_state,
            events=events,
            outcomes=outcomes
        )