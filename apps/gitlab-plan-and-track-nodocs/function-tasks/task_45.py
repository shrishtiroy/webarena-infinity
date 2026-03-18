import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    parent = next((e for e in state["epics"] if e["title"] == "API v3 Migration"), None)
    if not parent:
        return False, "Parent epic 'API v3 Migration' not found."

    child = next((e for e in state["epics"] if e["title"] == "API v3 - Deprecated Endpoints"), None)
    if not child:
        return False, "Child epic 'API v3 - Deprecated Endpoints' not found."

    if child["parentEpicId"] != parent["id"]:
        return False, f"Expected parentEpicId {parent['id']}, got {child['parentEpicId']}."

    return True, "Child epic 'API v3 - Deprecated Endpoints' created under 'API v3 Migration'."
