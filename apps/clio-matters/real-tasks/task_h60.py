import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Nguyen matter
    nguyen = None
    for m in state.get("matters", []):
        if "Nguyen" in (m.get("description") or ""):
            nguyen = m
            break
    if not nguyen:
        return False, "Nguyen divorce case not found."

    # Find expected user IDs
    thompson = None
    garcia = None
    for u in state.get("firmUsers", []):
        if u.get("fullName") == "Rachel Thompson":
            thompson = u
        elif u.get("fullName") == "Maria Garcia":
            garcia = u

    if not thompson:
        return False, "Rachel Thompson not found."
    if not garcia:
        return False, "Maria Garcia not found."

    # Find Trial/Hearing stage in Family Law
    fl_id = None
    for pa in state.get("practiceAreas", []):
        if pa.get("name") == "Family Law":
            fl_id = pa.get("id")
            break
    if not fl_id:
        return False, "Family Law practice area not found."

    stages = state.get("matterStages", {}).get(fl_id, [])
    trial_stage = next(
        (s for s in stages if s.get("name") == "Trial/Hearing"), None
    )
    if not trial_stage:
        return False, "Trial/Hearing stage not found in Family Law."

    errors = []

    if nguyen.get("status") != "Open":
        errors.append(f"Status is '{nguyen.get('status')}', expected 'Open'.")

    if nguyen.get("responsibleStaffId") != thompson["id"]:
        errors.append(
            f"Responsible staff is '{nguyen.get('responsibleStaffId')}', "
            f"expected '{thompson['id']}' (Rachel Thompson)."
        )

    bp = nguyen.get("billingPreference", {})
    if bp.get("billingMethod") != "contingency":
        errors.append(
            f"Billing method is '{bp.get('billingMethod')}', expected 'contingency'."
        )
    rate = bp.get("contingencyRate")
    if rate is None or abs(rate - 35) > 0.02:
        errors.append(f"Contingency rate is {rate}, expected 35.")
    if bp.get("contingencyRecipientId") != garcia["id"]:
        errors.append(
            f"Contingency recipient is '{bp.get('contingencyRecipientId')}', "
            f"expected '{garcia['id']}' (Maria Garcia)."
        )

    if nguyen.get("matterStageId") != trial_stage["id"]:
        actual_stage = next(
            (s["name"] for s in stages if s["id"] == nguyen.get("matterStageId")),
            nguyen.get("matterStageId"),
        )
        errors.append(
            f"Stage is '{actual_stage}', expected 'Trial/Hearing'."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Nguyen case: reopened, staff=Thompson, contingency 35% (Garcia), Trial/Hearing stage."
