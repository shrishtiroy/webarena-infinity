import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # These three should be recovered from bin and closed:
    # del_matter_2 (Test Matter), del_matter_5 (Template Matter), del_matter_6 (Jones inquiry)
    targets = {
        "del_matter_2": "test matter",
        "del_matter_5": "template matter",
        "del_matter_6": "jones",
    }

    # Check they are NOT in deletedMatters anymore
    deleted_ids = {dm["id"] for dm in state.get("deletedMatters", [])}
    for tid, desc in targets.items():
        if tid in deleted_ids:
            errors.append(f"{tid} ({desc}) is still in the recovery bin.")

    # Check they ARE in matters list and are closed
    matters = state.get("matters", [])
    for tid, desc_kw in targets.items():
        found = next(
            (m for m in matters
             if m.get("id") == tid
             or (desc_kw in m.get("description", "").lower()
                 and m.get("id", "").startswith("del_"))),
            None,
        )
        if found is None:
            # Search more broadly
            found = next(
                (m for m in matters
                 if desc_kw in m.get("description", "").lower()),
                None,
            )
        if found is None:
            errors.append(f"{tid} ({desc_kw}) not found in active matters list.")
        elif found.get("status") != "closed":
            errors.append(
                f"{found.get('description', tid)} status is '{found.get('status')}', "
                f"expected 'closed'."
            )

    if errors:
        return False, "Recovery and closure not complete. " + " | ".join(errors)

    return True, (
        "All three matters (Test Matter, Template Matter, Jones Inquiry) "
        "recovered from bin and closed successfully."
    )
