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

    if matter.get("openDate") != "2024-12-01":
        return False, f"Expected matter '00010-Dimitriou' openDate to be '2024-12-01', but got '{matter.get('openDate')}'."

    return True, "Matter '00010-Dimitriou' openDate is correctly set to '2024-12-01'."
