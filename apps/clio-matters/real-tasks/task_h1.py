import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # The open PI matters that should now be Closed:
    # mat_001 (Rodriguez), mat_002 (Foster), mat_008 (Cruz), mat_013 (Harris)
    # mat_012 (O'Brien) was already Closed, so we don't require changes on it.
    target_ids = {"mat_001", "mat_002", "mat_008", "mat_013"}
    found = {}

    for matter in matters:
        mid = matter.get("id", "")
        pa = matter.get("practiceAreaId", "")
        if mid in target_ids:
            found[mid] = matter.get("status", "")

    errors = []
    for mid in target_ids:
        if mid not in found:
            errors.append(f"Matter {mid} not found in matters list")
        elif found[mid] != "Closed":
            errors.append(f"Matter {mid} status is '{found[mid]}', expected 'Closed'")

    if errors:
        return False, "; ".join(errors)

    return True, "All four previously-open Personal Injury cases (Rodriguez, Foster, Cruz, Harris) are now Closed."
