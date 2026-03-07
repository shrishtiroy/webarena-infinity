import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    stages = state.get("matterStages", {})

    # Find Initial Consultation stage for PI (pa_001)
    pi_stages = stages.get("pa_001", [])
    ic_stage_id = None
    for stg in pi_stages:
        if stg.get("name", "").lower() == "initial consultation":
            ic_stage_id = stg.get("id", "")
            break

    if not ic_stage_id:
        return False, "Could not find an 'Initial Consultation' stage for Personal Injury practice area."

    # Find Kowalski matter
    kowalski = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Kowalski" in desc or mid == "mat_014":
            kowalski = matter
            break

    if not kowalski:
        return False, "Could not find the Kowalski matter in state."

    errors = []

    # Check practiceAreaId == pa_001
    if kowalski.get("practiceAreaId") != "pa_001":
        errors.append(f"practiceAreaId is '{kowalski.get('practiceAreaId')}', expected 'pa_001' (Personal Injury)")

    # Check matterStageId == Initial Consultation
    if kowalski.get("matterStageId") != ic_stage_id:
        errors.append(f"matterStageId is '{kowalski.get('matterStageId')}', expected '{ic_stage_id}' (Initial Consultation)")

    if errors:
        return False, "; ".join(errors)

    return True, "Kowalski matter moved to Personal Injury practice area at Initial Consultation stage."
