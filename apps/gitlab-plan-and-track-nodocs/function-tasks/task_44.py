import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    epic = next((e for e in state["epics"] if e["title"] == "Data Export/Import Feature"), None)
    if not epic:
        return False, "Epic 'Data Export/Import Feature' not found."

    if epic["state"] != "opened":
        return False, f"Expected state 'opened', got '{epic['state']}'."

    return True, "Epic 'Data Export/Import Feature' reopened."
