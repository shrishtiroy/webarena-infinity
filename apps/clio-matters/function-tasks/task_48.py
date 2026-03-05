import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00010"]
    if not matching:
        return False, "Matter with number '00010' not found."

    matter = matching[0]
    client_id = matter.get("clientId")
    if client_id != "contact_61":
        return False, f"Expected matter '00010' clientId 'contact_61' (Nancy Whitfield), got '{client_id}'."

    return True, "Matter '00010-Dimitriou' clientId is correctly set to 'contact_61' (Nancy Whitfield)."
