from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BeliefRevisionResult:

    # ---------------------------------
    # Belief being revised
    # ---------------------------------

    belief_id: str

    # ---------------------------------
    # Previous belief state
    # ---------------------------------

    previous_status: str

    # ---------------------------------
    # New belief state
    # ---------------------------------

    new_status: str

    # ---------------------------------
    # Why the belief changed
    # ---------------------------------

    revision_type: str

    reason: str

    # ---------------------------------
    # Evidence involved in revision
    # ---------------------------------

    evidence_ids: list[str] = field(
        default_factory=list
    )

    # ---------------------------------
    # Additional information
    # ---------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ---------------------------------
    # Timestamp
    # ---------------------------------

    timestamp: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )


class BeliefRevisionEngine:

    # ---------------------------------
    # Revise a belief based on the
    # current verification result
    # ---------------------------------

    def revise(
        self,
        belief,
        consensus_status: str,
        evidence_ids: list[str] | None = None
    ):

        previous_status = belief.status

        new_status = self._determine_status(
            consensus_status
        )

        revision_type = (
            self._determine_revision_type(
                previous_status,
                new_status
            )
        )

        reason = self._build_reason(
            previous_status,
            new_status,
            consensus_status
        )

        if evidence_ids is None:
            evidence_ids = []

        # Update the actual belief
        belief.update(
            status=new_status,
            evidence_ids=evidence_ids,
            verification_status=(
                consensus_status.lower()
            )
        )

        return BeliefRevisionResult(
            belief_id=belief.belief_id,
            previous_status=previous_status,
            new_status=new_status,
            revision_type=revision_type,
            reason=reason,
            evidence_ids=evidence_ids,
            metadata={
                "consensus_status":
                    consensus_status
            }
        )

    # ---------------------------------
    # Simulation-driven belief revision
    # ---------------------------------

    def revise_from_simulation(
        self,
        belief,
        hypothesis_evaluation: dict[str, Any],
        evidence_ids: list[str] | None = None
    ):

        previous_status = belief.status

        evaluation_status = (
            hypothesis_evaluation.get(
                "evaluation_status",
                "needs_review"
            )
        )

        new_status = (
            self._determine_simulation_status(
                evaluation_status
            )
        )

        revision_type = (
            self._determine_revision_type(
                previous_status,
                new_status
            )
        )

        reason = self._build_simulation_reason(
            previous_status,
            new_status,
            evaluation_status,
            hypothesis_evaluation.get(
                "reason",
                ""
            )
        )

        if evidence_ids is None:
            evidence_ids = []

        # Update the actual belief using the
        # result of the simulation evaluation.
        belief.update(
            status=new_status,
            evidence_ids=evidence_ids,
            verification_status=(
                f"simulation_{evaluation_status}"
            )
        )

        return BeliefRevisionResult(
            belief_id=belief.belief_id,
            previous_status=previous_status,
            new_status=new_status,
            revision_type=revision_type,
            reason=reason,
            evidence_ids=evidence_ids,
            metadata={
                "revision_source":
                    "simulation",
                "evaluation_status":
                    evaluation_status,
                "simulation_scenario_id":
                    hypothesis_evaluation.get(
                        "simulation_scenario_id"
                    ),
                "outcome_count":
                    hypothesis_evaluation.get(
                        "outcome_count",
                        0
                    ),
                "simulation_completed":
                    hypothesis_evaluation.get(
                        "simulation_completed",
                        False
                    ),
                "evaluation_reason":
                    hypothesis_evaluation.get(
                        "reason",
                        ""
                    )
            }
        )

    # ---------------------------------
    # Map consensus to belief status
    # ---------------------------------

    def _determine_status(
        self,
        consensus_status: str
    ):

        status_mapping = {
            "Verified": "supported",
            "Needs Review": "needs_review",
            "Inconsistent": "inconsistent"
        }

        return status_mapping.get(
            consensus_status,
            "unknown"
        )

    # ---------------------------------
    # Map simulation evaluation to
    # belief status
    # ---------------------------------

    def _determine_simulation_status(
        self,
        evaluation_status: str
    ):

        status_mapping = {
            "supported": "supported",
            "needs_review": "needs_review",
            "contradicted": "inconsistent",
            "proposed": "needs_review"
        }

        return status_mapping.get(
            evaluation_status,
            "needs_review"
        )

    # ---------------------------------
    # Determine how the belief changed
    # ---------------------------------

    def _determine_revision_type(
        self,
        previous_status: str,
        new_status: str
    ):

        if previous_status == new_status:
            return "unchanged"

        if (
            previous_status == "supported"
            and new_status in {
                "needs_review",
                "inconsistent"
            }
        ):
            return "weakened"

        if (
            previous_status in {
                "unknown",
                "needs_review"
            }
            and new_status == "supported"
        ):
            return "strengthened"

        if new_status == "inconsistent":
            return "contradicted"

        return "updated"

    # ---------------------------------
    # Explain the revision
    # ---------------------------------

    def _build_reason(
        self,
        previous_status: str,
        new_status: str,
        consensus_status: str
    ):

        if previous_status == new_status:
            return (
                "The new verification result did not "
                "change the current belief status."
            )

        if new_status == "supported":
            return (
                "New verification evidence supports "
                "the belief."
            )

        if new_status == "needs_review":
            return (
                "The latest verification result does "
                "not provide sufficient support for "
                "the belief to remain fully supported."
            )

        if new_status == "inconsistent":
            return (
                "The latest verification result indicates "
                "that the belief is inconsistent with the "
                "available evidence."
            )

        return (
            f"The belief was updated from "
            f"{previous_status} to {new_status} "
            f"based on consensus status "
            f"{consensus_status}."
        )

    # ---------------------------------
    # Explain simulation-driven revision
    # ---------------------------------

    def _build_simulation_reason(
        self,
        previous_status: str,
        new_status: str,
        evaluation_status: str,
        evaluation_reason: str
    ):

        if previous_status == new_status:
            return (
                "The simulation evaluation did not "
                "change the current belief status. "
                f"Simulation evaluation status: "
                f"{evaluation_status}. "
                f"{evaluation_reason}"
            )

        if new_status == "supported":
            return (
                "Simulation evaluation supports "
                "strengthening the belief. "
                f"{evaluation_reason}"
            )

        if new_status == "needs_review":
            return (
                "Simulation evaluation does not provide "
                "sufficient support for the belief to remain "
                "fully supported. "
                f"{evaluation_reason}"
            )

        if new_status == "inconsistent":
            return (
                "Simulation evaluation indicates that "
                "the belief is inconsistent with the "
                "current reasoning state. "
                f"{evaluation_reason}"
            )

        return (
            f"The belief was updated from "
            f"{previous_status} to {new_status} "
            f"based on simulation evaluation "
            f"{evaluation_status}. "
            f"{evaluation_reason}"
        )