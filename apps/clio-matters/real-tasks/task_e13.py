import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering = state.get("numberingScheme", {})
    if not numbering:
        return False, "No numberingScheme found in state."

    next_number = numbering.get("nextMatterNumber")
    if next_number == 200:
        return True, "Next matter number is now 200."
    else:
        return False, f"nextMatterNumber is {next_number}, expected 200."
