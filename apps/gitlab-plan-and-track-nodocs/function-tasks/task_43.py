import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    epic = next((e for e in state["epics"] if e["title"] == "Documentation Revamp"), None)
    if not epic:
        return False, "Epic 'Documentation Revamp' not found."

    if epic["state"] != "closed":
        return False, f"Expected state 'closed', got '{epic['state']}'."

    return True, "Epic 'Documentation Revamp' closed."
