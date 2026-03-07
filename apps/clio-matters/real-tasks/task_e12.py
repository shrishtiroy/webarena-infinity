import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering = state.get("numberingScheme", {})
    if not numbering:
        return False, "No numberingScheme found in state."

    update_by_default = numbering.get("updateByDefault", False)
    if update_by_default is True:
        return True, "Auto-update numbering is now enabled (updateByDefault=true)."
    else:
        return False, f"updateByDefault is {update_by_default}, expected true."
