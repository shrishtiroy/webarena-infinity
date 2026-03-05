import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    for pa in practice_areas:
        if pa.get("name") == "Environmental Law":
            return False, "Practice area 'Environmental Law' still exists but should have been deleted."

    return True, "Practice area 'Environmental Law' has been successfully deleted."
