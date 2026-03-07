import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Michael Osei (usr_006) originally had these matters:
    # mat_002 (Foster), mat_005 (Nguyen), mat_007 (Singh), mat_011 (Mendez), mat_013 (Harris)
    # All should now have responsibleAttorneyId == 'usr_003' (Maria Garcia)
    target_ids = {"mat_002", "mat_005", "mat_007", "mat_011", "mat_013"}
    found = {}

    for matter in matters:
        mid = matter.get("id", "")
        if mid in target_ids:
            found[mid] = matter.get("responsibleAttorneyId", "")

    errors = []
    for mid in target_ids:
        if mid not in found:
            errors.append(f"Matter {mid} not found in matters list")
        elif found[mid] != "usr_003":
            errors.append(f"Matter {mid} responsibleAttorneyId is '{found[mid]}', expected 'usr_003' (Maria Garcia)")

    if errors:
        return False, "; ".join(errors)

    return True, "All 5 of Michael Osei's cases are now reassigned to Maria Garcia."
