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

    found_client_intake = False
    found_initial_consultation = False

    for stage in stages:
        if stage.get("name") == "Client Intake":
            found_client_intake = True
        if stage.get("name") == "Initial Consultation":
            found_initial_consultation = True

    if found_initial_consultation:
        return False, "Stage 'Initial Consultation' still exists; it should have been renamed or removed."
    if not found_client_intake:
        return False, "Stage 'Client Intake' not found in 'Personal Injury' stages."

    return True, "Stage 'Initial Consultation' renamed to 'Client Intake' successfully."
