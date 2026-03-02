import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the two Simmons PI matters
    # matter_13: Simmons v. Uber (budget=55000) — higher budget
    # matter_19: Simmons v. PetSmart (budget=20000, pending) — lower budget
    simmons_matters = [
        m for m in state.get("matters", [])
        if "simmons" in m.get("description", "").lower()
        and m.get("practiceAreaId") == "pa_1"
    ]

    if len(simmons_matters) < 1:
        # Check if one was deleted
        deleted = state.get("deletedMatters", [])
        simmons_deleted = [
            dm for dm in deleted
            if "simmons" in dm.get("description", "").lower()
        ]
        if not simmons_deleted:
            return False, "No Simmons PI matters found (neither active nor deleted)."

    # Identify higher and lower budget matters
    # Higher budget (matter_13, budget=55000) should have new general damage
    higher = next(
        (m for m in state.get("matters", []) if m.get("id") == "matter_13"),
        None
    )

    if higher is None:
        errors.append("matter_13 (Simmons v. Uber, higher budget) not found in active matters.")
    else:
        # Check for general damage ~$100,000
        damages = state.get("damages", [])
        matter_damages = [d for d in damages if d.get("matterId") == "matter_13"]
        has_pain_damage = any(
            d.get("type") == "general" and abs(float(d.get("amount", 0)) - 100000) < 10000
            for d in matter_damages
        )
        if not has_pain_damage:
            existing = [(d.get("name"), d.get("amount"), d.get("type")) for d in matter_damages]
            errors.append(
                f"No general damage ~$100,000 found on matter_13. "
                f"Existing damages: {existing}."
            )

    # Lower budget (matter_19, budget=20000) should have been deleted
    lower_active = next(
        (m for m in state.get("matters", []) if m.get("id") == "matter_19"),
        None
    )

    if lower_active is not None:
        errors.append(
            f"matter_19 (Simmons v. PetSmart, lower budget) is still in active matters "
            f"with status '{lower_active.get('status')}'. It should have been deleted."
        )
    else:
        # Verify it's in deleted matters
        deleted = state.get("deletedMatters", [])
        in_deleted = any(dm.get("id") == "matter_19" for dm in deleted)
        if not in_deleted:
            errors.append(
                "matter_19 (Simmons v. PetSmart) not found in active matters or deleted matters."
            )

    if errors:
        return False, "Simmons matters not handled correctly. " + " | ".join(errors)

    return True, (
        "Higher-budget Simmons matter (matter_13) has ~$100,000 general damage added. "
        "Lower-budget Simmons matter (matter_19) deleted successfully."
    )
