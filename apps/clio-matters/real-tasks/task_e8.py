import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])

    for pa in practice_areas:
        name = pa.get("name", "")
        if name == "Medical Malpractice":
            return False, "Medical Malpractice practice area still exists."

    return True, "Medical Malpractice practice area has been deleted."
