from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Hypothesis:

    # ---------------------------------
    # Hypothesis identity
    # ---------------------------------

    hypothesis_id: str

    # ---------------------------------
    # Proposed explanation
    # ---------------------------------

    statement: str

    # ---------------------------------
    # Current hypothesis status
    # ---------------------------------

    status: str = "proposed"

    # ---------------------------------
    # Evidence associated with hypothesis
    # ---------------------------------

    evidence_ids: list[str] = field(
        default_factory=list
    )

    # ---------------------------------
    # Entities associated with hypothesis
    # ---------------------------------

    entity_ids: list[str] = field(
        default_factory=list
    )

    # ---------------------------------
    # Supporting beliefs
    # ---------------------------------

    belief_ids: list[str] = field(
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

    created_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    updated_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    # ---------------------------------
    # Update hypothesis
    # ---------------------------------

    def update(
        self,
        status: str | None = None,
        evidence_ids: list[str] | None = None,
        entity_ids: list[str] | None = None,
        belief_ids: list[str] | None = None,
        verification_status: str | None = None
    ):

        if status is not None:
            self.status = status

        if evidence_ids is not None:
            self.evidence_ids = evidence_ids

        if entity_ids is not None:
            self.entity_ids = entity_ids

        if belief_ids is not None:
            self.belief_ids = belief_ids

        if verification_status is not None:
            self.verification_status = (
                verification_status
            )

        self.updated_at = (
            datetime.utcnow().isoformat()
        )