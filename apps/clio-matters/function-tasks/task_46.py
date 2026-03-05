import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00001"]
    if not matching:
        return False, "Matter with number '00001' not found."

    matter = matching[0]
    billing = matter.get("billing", {})
    currency = billing.get("currency")
    if currency != "EUR":
        return False, f"Expected matter '00001' billing currency 'EUR', got '{currency}'."

    return True, "Matter '00001-Patterson' billing currency is correctly set to 'EUR'."
