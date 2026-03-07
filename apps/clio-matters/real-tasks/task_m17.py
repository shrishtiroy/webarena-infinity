import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Lisa Patel user id
    firm_users = state.get("firmUsers", [])
    lisa_id = None
    for user in firm_users:
        name = user.get("fullName", "") or ""
        if name == "Lisa Patel":
            lisa_id = user.get("id", "")
            break
    if not lisa_id:
        lisa_id = "usr_009"

    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        name = tmpl.get("name", "") or ""
        if "Criminal Defense" in name and "Misdemeanor" in name:
            staff_id = tmpl.get("responsibleStaffId", "")
            if staff_id == lisa_id:
                return True, "Criminal Defense - Misdemeanor template responsibleStaffId updated to Lisa Patel."
            else:
                return False, f"Found Criminal Defense - Misdemeanor template but responsibleStaffId is '{staff_id}', expected '{lisa_id}' (Lisa Patel)."

    return False, "Could not find a template named 'Criminal Defense - Misdemeanor' in matterTemplates."
