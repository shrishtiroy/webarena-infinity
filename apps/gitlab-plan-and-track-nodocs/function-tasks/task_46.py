import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    epic = next((e for e in state["epics"] if e["title"] == "Dark Mode Implementation"), None)
    if not epic:
        return False, "Epic 'Dark Mode Implementation' not found."

    if epic["startDate"] != "2026-03-15":
        return False, f"Expected startDate '2026-03-15', got '{epic['startDate']}'."

    return True, "Epic 'Dark Mode Implementation' start date changed to 2026-03-15."
