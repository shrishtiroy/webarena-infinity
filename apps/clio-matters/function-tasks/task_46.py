import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    for pa in practice_areas:
        if pa.get("name") == "Medical Malpractice":
            return False, "Practice area 'Medical Malpractice' still exists; it should have been removed."

    return True, "Practice area 'Medical Malpractice' has been successfully removed."
