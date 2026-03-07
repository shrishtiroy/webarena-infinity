import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    if not practice_areas:
        return False, "No practice areas found in state."

    for pa in practice_areas:
        name = pa.get("name", "")
        if name == "Environmental Law":
            return True, "Environmental Law practice area exists."

    return False, "Environmental Law practice area not found."
