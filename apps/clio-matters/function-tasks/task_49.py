import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00009"]
    if not matching:
        return False, "Matter with number '00009' not found."

    matter = matching[0]
    status = matter.get("status")
    if status != "open":
        return False, f"Expected matter '00009' status 'open', got '{status}'."

    return True, "Matter '00009-Ababio' status is correctly set to 'open'."
