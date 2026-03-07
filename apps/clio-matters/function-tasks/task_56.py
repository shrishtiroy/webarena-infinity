import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    numbering_scheme = state.get("numberingScheme", {})
    next_matter_number = numbering_scheme.get("nextMatterNumber")

    if next_matter_number is None:
        return False, "numberingScheme.nextMatterNumber not found in state."
    if next_matter_number != 200:
        return False, f"numberingScheme.nextMatterNumber is {next_matter_number}, expected 200."

    return True, "numberingScheme.nextMatterNumber is correctly set to 200."
