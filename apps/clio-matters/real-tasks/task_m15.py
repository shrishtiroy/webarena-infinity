import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find David Kim user id
    firm_users = state.get("firmUsers", [])
    david_id = None
    lisa_id = None
    for user in firm_users:
        name = user.get("fullName", "") or ""
        if name == "David Kim":
            david_id = user.get("id", "")
        if name == "Lisa Patel":
            lisa_id = user.get("id", "")
    if not david_id:
        david_id = "usr_004"
    if not lisa_id:
        lisa_id = "usr_009"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Foster" in desc or matter_id == "mat_002":
            attorney = matter.get("responsibleAttorneyId", "")
            staff = matter.get("responsibleStaffId", "")
            errors = []
            if attorney != david_id:
                errors.append(f"responsibleAttorneyId is '{attorney}', expected '{david_id}' (David Kim)")
            if staff != lisa_id:
                errors.append(f"responsibleStaffId is '{staff}', expected '{lisa_id}' (Lisa Patel)")
            if errors:
                return False, f"Foster matter found but: {'; '.join(errors)}."
            return True, "Foster case updated: responsible attorney to David Kim, responsible staff to Lisa Patel."

    return False, "Could not find the Foster matter in state."
