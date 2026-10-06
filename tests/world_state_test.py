from world_state.manager import WorldStateManager


manager = WorldStateManager()


print("=" * 60)
print("CIF PERSISTENT WORLD STATE TEST")
print("=" * 60)


# ---------------------------------
# 1. Initial state
# ---------------------------------

print("\nInitial State")
print("-" * 60)

print(
    manager.get_summary()
)


# ---------------------------------
# 2. Add an entity
# ---------------------------------

manager.add_entity(
    entity_id="CVE-2026-0544",
    entity_type="Vulnerability",
    properties={
        "source": "NVD"
    }
)


# ---------------------------------
# 3. Add evidence
# ---------------------------------

manager.add_evidence({
    "id": "NVD-CVE-2026-0544",
    "source": "NVD",
    "claim":
        "CVE-2026-0544 is a SQL injection vulnerability."
})


# ---------------------------------
# 4. Add belief
# ---------------------------------

manager.set_belief(
    belief_id="belief-CVE-2026-0544",
    belief={
        "claim":
            "CVE-2026-0544 is a relevant vulnerability.",
        "status": "supported",
        "evidence_ids": [
            "NVD-CVE-2026-0544"
        ]
    }
)


# ---------------------------------
# 5. Add verification result
# ---------------------------------

manager.add_verification({
    "agent": "Consensus Agent",
    "status": "Verified",
    "reason":
        "Evidence, graph, and consistency checks agree."
})


# ---------------------------------
# 6. Display updated state
# ---------------------------------

print("\nUpdated State")
print("-" * 60)

print(
    manager.get_summary()
)


# ---------------------------------
# 7. Display stored belief
# ---------------------------------

print("\nStored Belief")
print("-" * 60)

print(
    manager.get_state().beliefs[
        "belief-CVE-2026-0544"
    ]
)


# ---------------------------------
# 8. Display verification
# ---------------------------------

print("\nVerification History")
print("-" * 60)

for verification in (
    manager.get_state().verification_history
):

    print(
        verification
    )