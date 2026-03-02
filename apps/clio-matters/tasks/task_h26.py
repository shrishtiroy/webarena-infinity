import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    matters = state.get("matters", [])
    deleted = state.get("deletedMatters", [])

    # The two duplicate matters that should have been recovered and closed:
    # del_matter_1: "TechStartup Inc. - Contract review (duplicate)"
    # del_matter_4: "Brennan v. Oceanview Hotel (duplicate entry)"
    target_ids = ["del_matter_1", "del_matter_4"]

    for target_id in target_ids:
        # Check it's no longer in recovery bin
        still_deleted = any(dm.get("id") == target_id for dm in deleted)
        if still_deleted:
            errors.append(f"{target_id} is still in the recovery bin (not recovered).")
            continue

        # Check it's in active matters and closed
        recovered = next((m for m in matters if m.get("id") == target_id), None)
        if recovered is None:
            # Also check by description patterns
            if target_id == "del_matter_1":
                recovered = next(
                    (m for m in matters
                     if "techstartup" in m.get("description", "").lower()
                     and "duplicate" in m.get("description", "").lower()),
                    None
                )
            elif target_id == "del_matter_4":
                recovered = next(
                    (m for m in matters
                     if "brennan" in m.get("description", "").lower()
                     and "oceanview" in m.get("description", "").lower()
                     and "duplicate" in m.get("description", "").lower()),
                    None
                )

        if recovered is None:
            errors.append(f"{target_id} was not found in active matters after recovery.")
            continue

        if recovered.get("status") != "closed":
            errors.append(
                f"{target_id} ('{recovered.get('description', '')}') has status "
                f"'{recovered.get('status')}', expected 'closed'."
            )

    if errors:
        return False, "Recovery bin matters not handled correctly. " + " | ".join(errors)

    return True, "Both duplicate matters recovered from bin and closed successfully."
