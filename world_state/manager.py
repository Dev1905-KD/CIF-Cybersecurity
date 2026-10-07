from datetime import datetime
from typing import Any

from world_state.state import WorldState


class WorldStateManager:

    def __init__(self):
        self.state = WorldState()

    # ---------------------------------
    # Entity management
    # ---------------------------------

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: dict[str, Any] | None = None
    ):
        self.state.entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "properties": properties or {},
            "updated_at": datetime.utcnow().isoformat()
        }

        self.state.increment_version()

    # ---------------------------------
    # Evidence management
    # ---------------------------------

    def add_evidence(
        self,
        evidence: dict[str, Any]
    ):
        if "id" not in evidence:
            evidence["id"] = (
                f"evidence-{len(self.state.evidence) + 1}"
            )

        evidence["created_at"] = (
            datetime.utcnow().isoformat()
        )

        self.state.evidence.append(
            evidence
        )

        self.state.increment_version()

        return evidence["id"]

    # ---------------------------------
    # Belief management
    # ---------------------------------

    def set_belief(
        self,
        belief_id: str,
        belief: dict[str, Any]
    ):
        belief["updated_at"] = (
            datetime.utcnow().isoformat()
        )

        self.state.beliefs[
            belief_id
        ] = belief

        self.state.increment_version()

    # ---------------------------------
    # Hypothesis management
    # ---------------------------------

    def add_hypothesis(
        self,
        hypothesis: dict[str, Any]
    ):
        self.state.hypotheses.append(
            hypothesis
        )

        self.state.increment_version()

    # ---------------------------------
    # Verification history
    # ---------------------------------

    def add_verification(
        self,
        verification: dict[str, Any]
    ):
        verification["timestamp"] = (
            datetime.utcnow().isoformat()
        )

        self.state.verification_history.append(
            verification
        )

        self.state.increment_version()

    def add_simulation(self, simulation: dict[str, Any]):
        simulation["timestamp"] = datetime.utcnow().isoformat()

        self.state.simulation_history.append(
            simulation
        )

        self.state.increment_version()

        return simulation
    
        

    # ---------------------------------
    # State access
    # ---------------------------------

    def get_state(self) -> WorldState:
        return self.state

    # ---------------------------------
    # State summary
    # ---------------------------------

    def get_summary(self) -> dict[str, Any]:

        return {
            "version": self.state.version,
            "last_updated": self.state.last_updated,
            "entity_count": len(
                self.state.entities
            ),
            "evidence_count": len(
                self.state.evidence
            ),
            "belief_count": len(
                self.state.beliefs
            ),
            "hypothesis_count": len(
                self.state.hypotheses
            ),
            "verification_count": len(
                self.state.verification_history
            ),
            "simulation_count": len(
                self.state.simulation_history
            )
        }