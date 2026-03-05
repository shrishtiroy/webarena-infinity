import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    damages = state.get("damages", [])
    for d in damages:
        if d.get("matterId") == "matter_1" and "emergency room visit" in d.get("name", "").lower():
            return False, f"Damage '{d['name']}' on matter_1 still exists but should have been deleted."

    return True, "Emergency room visit damage on matter_1 has been successfully deleted."
