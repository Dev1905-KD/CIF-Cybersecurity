from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WorldState:

    # ---------------------------------
    # Current entities known to CIF
    # ---------------------------------

    entities: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    # ---------------------------------
    # Evidence currently associated
    # with the world state
    # ---------------------------------

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ---------------------------------
    # Current beliefs maintained by CIF
    # ---------------------------------

    beliefs: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    # ---------------------------------
    # Current hypotheses
    # ---------------------------------

    hypotheses: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ---------------------------------
    # Verification history
    # ---------------------------------

    verification_history: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ---------------------------------
    # State metadata
    # ---------------------------------

    last_updated: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    version: int = 1

    def update_timestamp(self):
        self.last_updated = datetime.utcnow().isoformat()

    def increment_version(self):
        self.version += 1
        self.update_timestamp()