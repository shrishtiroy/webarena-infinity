import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    for pa in practice_areas:
        if pa.get("name") == "Civil Litigation":
            return True, "Practice area 'Civil Litigation' found."

    return False, "Practice area 'Civil Litigation' not found in practiceAreas."
