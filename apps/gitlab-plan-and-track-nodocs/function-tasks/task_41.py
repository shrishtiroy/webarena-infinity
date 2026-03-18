import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [e for e in state["epics"] if e["title"] == "GraphQL API Layer"]
    if not match:
        return False, "Epic 'GraphQL API Layer' not found."

    epic = match[0]
    if epic["state"] != "opened":
        return False, f"Expected state 'opened', got '{epic['state']}'."

    return True, "Epic 'GraphQL API Layer' created."
