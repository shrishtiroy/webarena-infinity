import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering = state.get("numberingScheme", {})
    padding = numbering.get("numberPadding")
    if padding != 6:
        return False, f"Expected numberingScheme numberPadding 6, got '{padding}'."

    return True, "Numbering scheme numberPadding is correctly set to 6."
