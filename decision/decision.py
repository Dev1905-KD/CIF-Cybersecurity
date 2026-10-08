from dataclasses import dataclass, field
from typing import Any


@dataclass
class Decision:
    decision_id: str
    status: str
    risk_level: str
    rationale: str
    recommended_actions: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    verification_status: str = "Unknown"
    hypothesis_status: str = "Unknown"
    simulation_status: str = "Unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "status": self.status,
            "risk_level": self.risk_level,
            "rationale": self.rationale,
            "recommended_actions": self.recommended_actions,
            "supporting_evidence": self.supporting_evidence,
            "verification_status": self.verification_status,
            "hypothesis_status": self.hypothesis_status,
            "simulation_status": self.simulation_status,
            "metadata": self.metadata,
        }