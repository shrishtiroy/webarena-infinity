import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    stages = state.get("matterStages", {})

    # Find Closing stage for Real Estate (pa_004)
    re_stages = stages.get("pa_004", [])
    closing_stage_id = None
    for stg in re_stages:
        if stg.get("name", "").lower() == "closing":
            closing_stage_id = stg.get("id", "")
            break

    if not closing_stage_id:
        return False, "Could not find a 'Closing' stage for Real Estate practice area."

    # Find Baker matter
    baker = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if ("Baker" in desc and "Residential" in desc) or mid == "mat_010":
            baker = matter
            break

    if not baker:
        return False, "Could not find the Baker - Residential Property matter in state."

    errors = []

    # Check 1: responsibleAttorneyId is still usr_007 (Jennifer Walsh)
    if baker.get("responsibleAttorneyId") != "usr_007":
        errors.append(f"responsibleAttorneyId is '{baker.get('responsibleAttorneyId')}', expected 'usr_007' (Jennifer Walsh)")

    # Check 2: matterStageId is Closing
    if baker.get("matterStageId") != closing_stage_id:
        errors.append(f"matterStageId is '{baker.get('matterStageId')}', expected '{closing_stage_id}' (Closing)")

    # Check 3: clientRefNumber == "RE-2026-FINAL"
    if baker.get("clientRefNumber") != "RE-2026-FINAL":
        errors.append(f"clientRefNumber is '{baker.get('clientRefNumber')}', expected 'RE-2026-FINAL'")

    if errors:
        return False, "; ".join(errors)

    return True, "Baker matter updated: attorney Jennifer Walsh, Closing stage, client ref RE-2026-FINAL."
