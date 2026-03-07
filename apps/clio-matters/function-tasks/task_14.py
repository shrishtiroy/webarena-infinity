import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find "Personal Injury" practice area ID
    practice_areas = state.get("practiceAreas", [])
    pi_id = None
    for pa in practice_areas:
        if pa.get("name", "") == "Personal Injury":
            pi_id = pa.get("id")
            break

    if pi_id is None:
        return False, "Could not find practice area named 'Personal Injury'."

    # Find "Mediation" stage ID within the Personal Injury stages
    matter_stages = state.get("matterStages", {})
    stages_for_pi = matter_stages.get(pi_id, [])
    mediation_stage_id = None
    for stage in stages_for_pi:
        if stage.get("name", "") == "Mediation":
            mediation_stage_id = stage.get("id")
            break

    if mediation_stage_id is None:
        return False, f"Could not find stage named 'Mediation' under Personal Injury practice area (id: {pi_id})."

    # Find the matter
    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Rodriguez v. Premier Auto" in desc:
            stage_id = matter.get("matterStageId", "")
            if stage_id == mediation_stage_id:
                return True, f"Matter '{desc}' has matterStageId '{mediation_stage_id}' (Mediation) as expected."
            else:
                return False, f"Matter '{desc}' has matterStageId '{stage_id}', expected '{mediation_stage_id}' (Mediation)."

    return False, "No matter found with description containing 'Rodriguez v. Premier Auto'."
