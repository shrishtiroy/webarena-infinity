import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering = state.get("numberingScheme", {})
    separator = numbering.get("separator")
    if separator != "/":
        return False, f"Expected numberingScheme separator '/', got '{separator}'."

    return True, "Numbering scheme separator is correctly set to '/'."
