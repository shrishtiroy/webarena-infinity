import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Criminal Law practice area id
    practice_areas = state.get("practiceAreas", [])
    criminal_id = None
    for pa in practice_areas:
        if pa.get("name") == "Criminal Law":
            criminal_id = pa.get("id", "")
            break
    if not criminal_id:
        criminal_id = "pa_002"

    # Check matterStages for Criminal Law
    matter_stages = state.get("matterStages", {})
    stages = matter_stages.get(criminal_id, [])
    for stage in stages:
        name = stage.get("name", "") or ""
        if name == "Expert Review":
            return True, "Expert Review stage added to Criminal Law practice area."

    return False, "No stage named 'Expert Review' found in Criminal Law matter stages."
