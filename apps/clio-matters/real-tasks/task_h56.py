import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    morales = None
    harris = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Morales" in desc and "Assault" in desc:
            morales = m
        elif "Harris" in desc and "Workplace" in desc:
            harris = m

    if not morales:
        return False, "Morales assault case not found."
    if not harris:
        return False, "Harris workplace injury case not found."

    errors = []

    # Morales should be on hold (Pending)
    if morales.get("status") != "Pending":
        errors.append(
            f"Morales status is '{morales.get('status')}', expected 'Pending'."
        )

    # Harris should have Morales's original responsible staff (usr_005, Rachel Thompson)
    # Morales seed: responsibleStaffId = 'usr_005'
    morales_staff = morales.get("responsibleStaffId")
    if harris.get("responsibleStaffId") != morales_staff:
        errors.append(
            f"Harris responsible staff is '{harris.get('responsibleStaffId')}', "
            f"expected '{morales_staff}' (Morales's staff)."
        )

    # Harris should be at Demand Letter stage
    pi_id = None
    for pa in state.get("practiceAreas", []):
        if pa.get("name") == "Personal Injury":
            pi_id = pa.get("id")
            break

    if pi_id:
        stages = state.get("matterStages", {}).get(pi_id, [])
        demand_stage = next(
            (s for s in stages if s.get("name") == "Demand Letter"), None
        )
        if demand_stage and harris.get("matterStageId") != demand_stage["id"]:
            actual_stage = next(
                (s["name"] for s in stages if s["id"] == harris.get("matterStageId")),
                harris.get("matterStageId"),
            )
            errors.append(
                f"Harris stage is '{actual_stage}', expected 'Demand Letter'."
            )

    if errors:
        return False, " ".join(errors)

    return True, "Morales on hold, staff transferred to Harris, Harris moved to Demand Letter."
