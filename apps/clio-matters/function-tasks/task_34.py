import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    names = [pa.get("name") for pa in practice_areas]

    if "Corporate/Business" in names:
        return False, "Practice area 'Corporate/Business' still exists and should have been renamed."

    if "Corporate & Transactional" not in names:
        return False, (
            f"Practice area 'Corporate & Transactional' not found. "
            f"Existing practice areas: {names}"
        )

    return True, "Practice area successfully renamed from 'Corporate/Business' to 'Corporate & Transactional'."
