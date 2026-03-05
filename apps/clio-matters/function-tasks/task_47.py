import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00005"]
    if not matching:
        return False, "Matter with number '00005' not found."

    matter = matching[0]
    originating = matter.get("originatingAttorneyId")
    if originating != "user_1":
        return False, f"Expected matter '00005' originatingAttorneyId 'user_1' (Sarah Chen), got '{originating}'."

    return True, "Matter '00005-Doyle' originatingAttorneyId is correctly set to 'user_1' (Sarah Chen)."
