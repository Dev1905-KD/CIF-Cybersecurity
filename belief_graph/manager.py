import re

from belief_graph.belief import Belief
from world_state.manager import WorldStateManager


class BeliefGraphManager:

    def __init__(
        self,
        world_state: WorldStateManager
    ):
        self.world_state = world_state
        self.beliefs: dict[str, Belief] = {}

    # ---------------------------------
    # Create or retrieve belief
    # ---------------------------------

    def get_or_create_belief(
        self,
        belief_id: str,
        claim: str
    ) -> Belief:

        if belief_id not in self.beliefs:

            self.beliefs[belief_id] = Belief(
                belief_id=belief_id,
                claim=claim
            )

        return self.beliefs[belief_id]

    # ---------------------------------
    # Update belief
    # ---------------------------------

    def update_belief(
        self,
        belief_id: str,
        status: str | None = None,
        evidence_ids: list[str] | None = None,
        entity_ids: list[str] | None = None,
        verification_status: str | None = None
    ):

        belief = self.beliefs.get(belief_id)

        if belief is None:
            return None

        belief.update(
            status=status,
            evidence_ids=evidence_ids,
            entity_ids=entity_ids,
            verification_status=verification_status
        )

        self._sync_to_world_state(belief)

        return belief

    # ---------------------------------
    # Create belief from verification
    # ---------------------------------

    def update_from_verification(
        self,
        query: str,
        answer: str,
        consensus_result: dict
    ):

        cves = self._extract_cves(
            query + "\n" + answer
        )

        if not cves:
            return []

        consensus_status = consensus_result.get(
            "status",
            "Needs Review"
        )

        status_mapping = {
            "Verified": "supported",
            "Needs Review": "needs_review",
            "Inconsistent": "inconsistent"
        }

        belief_status = status_mapping.get(
            consensus_status,
            "unknown"
        )

        verification_status = (
            consensus_status.lower()
        )

        updated_beliefs = []

        for cve in cves:

            belief_id = (
                f"belief-{cve.lower()}-relevance"
            )

            claim = (
                f"{cve} is relevant to the investigation."
            )

            belief = self.get_or_create_belief(
                belief_id,
                claim
            )
            self.world_state.add_entity(
                entity_id=cve,
                entity_type="Vulnerability",
                properties={
                    "source": "Knowledge Graph",
                    "belief_id": belief_id
                }
            )
            belief.update(
                status=belief_status,
                entity_ids=[cve],
                verification_status=verification_status
            )

            self._sync_to_world_state(
                belief
            )

            updated_beliefs.append(
                belief
            )

        return updated_beliefs

    # ---------------------------------
    # Sync belief with World State
    # ---------------------------------

    def _sync_to_world_state(
        self,
        belief: Belief
    ):

        self.world_state.set_belief(
            belief.belief_id,
            {
                "belief_id": belief.belief_id,
                "claim": belief.claim,
                "status": belief.status,
                "evidence_ids": belief.evidence_ids,
                "entity_ids": belief.entity_ids,
                "verification_status":
                    belief.verification_status,
                "metadata": belief.metadata,
                "updated_at": belief.updated_at
            }
        )

    # ---------------------------------
    # Extract CVE identifiers
    # ---------------------------------

    def _extract_cves(
        self,
        text: str
    ):

        return list(
            dict.fromkeys(
                re.findall(
                    r"CVE-\d{4}-\d{4,7}",
                    text.upper()
                )
            )
        )

    # ---------------------------------
    # Get all beliefs
    # ---------------------------------

    def get_beliefs(self):

        return list(
            self.beliefs.values()
        )

    # ---------------------------------
    # Get serializable beliefs
    # ---------------------------------

    def get_belief_summary(self):

        return [
            {
                "belief_id": belief.belief_id,
                "claim": belief.claim,
                "status": belief.status,
                "entity_ids": belief.entity_ids,
                "verification_status":
                    belief.verification_status
            }
            for belief in self.beliefs.values()
        ]