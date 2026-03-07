import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Investigation stage ID for Personal Injury
    practice_areas = state.get("practiceAreas", [])
    pi_pa = next((pa for pa in practice_areas if pa.get("name") == "Personal Injury"), None)
    if not pi_pa:
        return False, "Personal Injury practice area not found."

    pi_id = pi_pa["id"]
    stages = state.get("matterStages", {}).get(pi_id, [])
    investigation_stage_id = None
    for stage in stages:
        if stage.get("name") == "Investigation":
            investigation_stage_id = stage.get("id")
            break

    if not investigation_stage_id:
        return False, "Investigation stage not found for Personal Injury."

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if ("Cruz" in desc and "Metro Transit" in desc) or matter_id == "mat_008":
            current_stage = matter.get("matterStageId", "")
            if current_stage == investigation_stage_id:
                return True, f"Cruz v. Metro Transit is now at Investigation stage ({investigation_stage_id})."
            else:
                return False, f"Cruz v. Metro Transit matterStageId is '{current_stage}', expected '{investigation_stage_id}'."

    return False, "Could not find the Cruz v. Metro Transit matter in state."
