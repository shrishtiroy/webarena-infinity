import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    stages = state.get("matterStages", {})

    # Find Mediation stage for PI (pa_001)
    pi_stages = stages.get("pa_001", [])
    mediation_stage_id = None
    for stg in pi_stages:
        if stg.get("name", "").lower() == "mediation":
            mediation_stage_id = stg.get("id", "")
            break

    if not mediation_stage_id:
        return False, "Could not find a 'Mediation' stage for Personal Injury practice area."

    # Find Rodriguez matter
    rodriguez = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Rodriguez" in desc or mid == "mat_001":
            rodriguez = matter
            break

    if not rodriguez:
        return False, "Could not find the Rodriguez matter in state."

    errors = []

    # Check 1: matterStageId == mediation
    actual_stage = rodriguez.get("matterStageId", "")
    if actual_stage != mediation_stage_id:
        errors.append(f"matterStageId is '{actual_stage}', expected '{mediation_stage_id}' (Mediation)")

    # Check 2: deductionOrder == expenses_first
    deduction = rodriguez.get("deductionOrder", "")
    if deduction != "expenses_first":
        errors.append(f"deductionOrder is '{deduction}', expected 'expenses_first'")

    # Check 3: Lakeside (con_014) recovery amount == 225000
    settlement = rodriguez.get("settlement", {})
    recoveries = settlement.get("recoveries", [])
    lakeside_found = False
    for rec in recoveries:
        if rec.get("sourceContactId") == "con_014":
            lakeside_found = True
            amt = rec.get("amount", 0)
            if amt != 225000:
                errors.append(f"Lakeside recovery amount is {amt}, expected 225000")
            break

    if not lakeside_found:
        errors.append("No recovery found for Lakeside Insurance (con_014)")

    if errors:
        return False, "; ".join(errors)

    return True, "Rodriguez moved to Mediation, deduction order set to expenses_first, Lakeside recovery updated to $225,000."
