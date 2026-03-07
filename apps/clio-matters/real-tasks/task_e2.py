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
        if "Midwest Manufacturing" in desc or matter_id == "mat_006":
            status = matter.get("status", "")
            if status == "Open":
                return True, "Midwest Manufacturing case is now Open."
            else:
                return False, f"Midwest Manufacturing case status is '{status}', expected 'Open'."

    return False, "Could not find the Midwest Manufacturing matter in state."
