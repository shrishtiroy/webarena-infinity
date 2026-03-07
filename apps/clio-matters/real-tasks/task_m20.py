import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Advanced Imaging Associates contact id
    contacts = state.get("contacts", [])
    aia_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Advanced Imaging" in name:
            aia_id = contact.get("id", "")
            break
    if not aia_id:
        aia_id = "con_020"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            providers = matter.get("medicalProviders", [])
            for provider in providers:
                if provider.get("contactId") == aia_id:
                    return False, "Advanced Imaging Associates is still present in Rodriguez medicalProviders. Expected it to be removed."
            return True, "Advanced Imaging Associates has been removed from Rodriguez medicalProviders."

    return False, "Could not find the Rodriguez matter in state."
