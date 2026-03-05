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
    stage_id = matter.get("stageId")
    if stage_id != "stage_1_2":
        return False, f"Expected matter '00010' stageId 'stage_1_2' (Investigation), got '{stage_id}'."

    return True, "Matter '00010-Dimitriou' stageId is correctly set to 'stage_1_2' (Investigation)."
