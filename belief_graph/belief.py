from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Belief:

    # ---------------------------------
    # Belief identity
    # ---------------------------------

    belief_id: str

    # ---------------------------------
    # What CIF currently believes
    # ---------------------------------

    claim: str

    # ---------------------------------
    # Belief state
    # ---------------------------------

    status: str = "unknown"

    # ---------------------------------
    # Evidence supporting the belief
    # ---------------------------------

    evidence_ids: list[str] = field(
        default_factory=list
    )

    # ---------------------------------
    # Entities associated with belief
    # ---------------------------------

    entity_ids: list[str] = field(
        default_factory=list
    )

    # ---------------------------------
    # Verification information
    # ---------------------------------

    verification_status: str = "unverified"

    # ---------------------------------
    # Additional metadata
    # ---------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ---------------------------------
    # Timestamp
    # ---------------------------------

    updated_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    def update(
        self,
        status: str | None = None,
        evidence_ids: list[str] | None = None,
        entity_ids: list[str] | None = None,
        verification_status: str | None = None
    ):

        if status is not None:
            self.status = status

        if evidence_ids is not None:
            self.evidence_ids = evidence_ids

        if entity_ids is not None:
            self.entity_ids = entity_ids

        if verification_status is not None:
            self.verification_status = (
                verification_status
            )

        self.updated_at = (
            datetime.utcnow().isoformat()
        )