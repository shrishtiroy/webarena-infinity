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
        if "Okafor" in desc or matter_id == "mat_004":
            status = matter.get("status", "")
            if status == "Pending":
                return True, "Okafor DUI case is now Pending."
            else:
                return False, f"Okafor DUI case status is '{status}', expected 'Pending'."

    return False, "Could not find the Okafor DUI matter in state."
