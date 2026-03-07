import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Criminal Law matters: mat_004 (Okafor), mat_015 (Morales). Both should be Pending.
    target_ids = {"mat_004", "mat_015"}
    found = {}

    for matter in matters:
        mid = matter.get("id", "")
        if mid in target_ids:
            found[mid] = matter.get("status", "")

    errors = []
    for mid in target_ids:
        if mid not in found:
            errors.append(f"Matter {mid} not found in matters list")
        elif found[mid] != "Pending":
            errors.append(f"Matter {mid} status is '{found[mid]}', expected 'Pending'")

    if errors:
        return False, "; ".join(errors)

    return True, "Both Criminal Law cases (Okafor, Morales) are now on hold (Pending)."
