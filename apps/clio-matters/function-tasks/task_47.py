import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    criminal_law = None
    personal_injury = None

    for pa in practice_areas:
        if pa.get("name") == "Criminal Law":
            criminal_law = pa
        if pa.get("name") == "Personal Injury":
            personal_injury = pa

    if criminal_law is None:
        return False, "Practice area 'Criminal Law' not found."
    if not criminal_law.get("isPrimary"):
        return False, "Practice area 'Criminal Law' is not set as primary."

    if personal_injury is None:
        return False, "Practice area 'Personal Injury' not found."
    if personal_injury.get("isPrimary"):
        return False, "Practice area 'Personal Injury' is still set as primary; it should no longer be primary."

    return True, "'Criminal Law' is now primary and 'Personal Injury' is no longer primary."
