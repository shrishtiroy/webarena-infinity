import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Personal Injury practice area (pa_001)
    practice_areas = state.get("practiceAreas", [])
    pi_pa = None
    for pa in practice_areas:
        pa_id = pa.get("id", "")
        pa_name = pa.get("name", "")
        if pa_id == "pa_001" or pa_name == "Personal Injury":
            pi_pa = pa
            break

    if not pi_pa:
        return False, "Personal Injury practice area not found in state."

    pi_id = pi_pa.get("id", "pa_001")
    stages = state.get("matterStages", {}).get(pi_id, [])
    if not stages:
        return False, "No stages found for Personal Injury practice area."

    stage_names = [s.get("name", "") for s in stages]

    if "Client Intake" not in stage_names:
        return False, f"'Client Intake' stage not found in Personal Injury stages. Found: {stage_names}"

    if "Initial Consultation" in stage_names:
        return False, "'Initial Consultation' stage still exists in Personal Injury stages (expected it to be renamed to 'Client Intake')."

    return True, "Initial Consultation has been renamed to Client Intake in Personal Injury stages."
