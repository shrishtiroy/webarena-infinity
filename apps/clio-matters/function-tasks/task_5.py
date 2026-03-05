import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00004":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00004'."

    if matter.get("responsibleAttorneyId") != "user_2":
        return False, f"Expected matter '00004-Washington' responsibleAttorneyId to be 'user_2' (Marcus Williams), but got '{matter.get('responsibleAttorneyId')}'."

    return True, "Matter '00004-Washington' responsibleAttorneyId is correctly set to 'user_2' (Marcus Williams)."
