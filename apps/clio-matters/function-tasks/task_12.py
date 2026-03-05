import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00010":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00010'."

    if matter.get("clientReferenceNumber") != "PI-2024-0601-REV":
        return False, f"Expected matter '00010-Dimitriou' clientReferenceNumber to be 'PI-2024-0601-REV', but got '{matter.get('clientReferenceNumber')}'."

    return True, "Matter '00010-Dimitriou' clientReferenceNumber is correctly set to 'PI-2024-0601-REV'."
