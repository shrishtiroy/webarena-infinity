import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    pa_id = None
    for pa in practice_areas:
        if pa.get("name") == "Personal Injury":
            pa_id = pa.get("id")
            break

    if pa_id is None:
        return False, "Practice area 'Personal Injury' not found."

    matter_stages = state.get("matterStages", {})
    stages = matter_stages.get(pa_id, [])

    for stage in stages:
        if stage.get("name") == "Case Review":
            return True, "Stage 'Case Review' found in 'Personal Injury' stages."

    return False, "Stage 'Case Review' not found in 'Personal Injury' stages."
