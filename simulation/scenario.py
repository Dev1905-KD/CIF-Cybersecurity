from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SimulationScenario:
    scenario_id: str
    title: str
    description: str
    entities: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    initial_beliefs: list[str] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: dict[str, Any] | None = None
    ):
        self.entities.append({
            "id": entity_id,
            "type": entity_type,
            "properties": properties or {}
        })

    def add_assumption(self, assumption: str):
        self.assumptions.append(assumption)

    def add_initial_belief(self, belief_id: str):
        self.initial_beliefs.append(belief_id)

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value
@dataclass
class SimulationEvent:
    event_type: str
    description: str
    entity_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


@dataclass
class SimulationOutcome:
    outcome_id: str
    status: str
    description: str
    affected_beliefs: list[str] = field(default_factory=list)
    affected_entities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)        