class ConsensusAgent:

    def evaluate(
        self,
        evidence_result,
        graph_result,
        consistency_result
    ):

        agent_results = {
            "Evidence Agent": evidence_result,
            "Graph Agent": graph_result,
            "Consistency Agent": consistency_result
        }

        statuses = {
            name: result.get("status", "Unknown")
            for name, result in agent_results.items()
        }

        conflicts = []

        # ---------------------------------
        # Evidence vs Consistency
        # ---------------------------------

        evidence_status = statuses["Evidence Agent"]
        consistency_status = statuses[
            "Consistency Agent"
        ]

        if (
            evidence_status == "Supported"
            and consistency_status == "Inconsistent"
        ):

            conflicts.append({
                "agents": [
                    "Evidence Agent",
                    "Consistency Agent"
                ],
                "type": "Verification Conflict",
                "message":
                    "Evidence supports the generated claims, "
                    "but the answer is inconsistent with "
                    "the retrieved context."
            })

        # ---------------------------------
        # Graph verification
        # ---------------------------------

        graph_status = statuses["Graph Agent"]

        if (
            graph_status == "Needs Review"
            and evidence_status == "Supported"
        ):

            conflicts.append({
                "agents": [
                    "Graph Agent",
                    "Evidence Agent"
                ],
                "type": "Graph Evidence Conflict",
                "message":
                    "The evidence supports the answer, "
                    "but one or more referenced entities "
                    "could not be verified in the Knowledge Graph."
            })

        # ---------------------------------
        # Determine final status
        # ---------------------------------

        if (
            evidence_status == "Needs Review"
            or evidence_status == "Partially Supported"
        ):

            final_status = "Needs Review"

        elif (
            evidence_status == "Supported"
            and graph_status == "Supported"
            and consistency_status == "Consistent"
        ):

            final_status = "Verified"

        elif (
            graph_status == "Needs Review"
            or consistency_status == "Needs Review"
        ):

            final_status = "Needs Review"

        elif consistency_status == "Inconsistent":

            final_status = "Inconsistent"

        else:

            final_status = "Needs Review"

        # ---------------------------------
        # Verification summary
        # ---------------------------------

        return {
            "agent": "Consensus Agent",
            "status": final_status,
            "agent_results": agent_results,
            "conflicts": conflicts,
            "verification": {
                "evidence": evidence_status,
                "graph": graph_status,
                "consistency": consistency_status
            }
        }