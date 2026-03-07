import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    pa_id = None
    for pa in practice_areas:
        if pa.get("name") == "Criminal Law":
            pa_id = pa.get("id")
            break

    if pa_id is None:
        return False, "Practice area 'Criminal Law' not found."

    matter_stages = state.get("matterStages", {})
    stages = matter_stages.get(pa_id, [])

    for stage in stages:
        if stage.get("name") == "Sentencing":
            return False, "Stage 'Sentencing' still exists in 'Criminal Law' stages; it should have been removed."

    return True, "Stage 'Sentencing' has been successfully removed from 'Criminal Law' stages."
