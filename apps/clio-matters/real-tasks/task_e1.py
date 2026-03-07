import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if "Nguyen" in desc or matter_id == "mat_005":
            status = matter.get("status", "")
            if status == "Closed":
                return True, "Nguyen divorce case is now Closed."
            else:
                return False, f"Nguyen divorce case status is '{status}', expected 'Closed'."

    return False, "Could not find the Nguyen divorce matter in state."
