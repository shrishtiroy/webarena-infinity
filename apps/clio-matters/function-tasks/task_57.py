import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering_scheme = state.get("numberingScheme", {})
    update_by_default = numbering_scheme.get("updateByDefault")

    if update_by_default is None:
        return False, "numberingScheme.updateByDefault not found in state."
    if update_by_default is not True:
        return False, f"numberingScheme.updateByDefault is {update_by_default}, expected True."

    return True, "numberingScheme.updateByDefault is correctly set to True."
