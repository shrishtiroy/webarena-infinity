import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    for pa in practice_areas:
        if pa.get("name") == "Civil Rights":
            return True, "Practice area 'Civil Rights' exists."

    return False, (
        f"Practice area 'Civil Rights' not found. "
        f"Existing practice areas: {[pa.get('name') for pa in practice_areas]}"
    )
