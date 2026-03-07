import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the firmUser with fullName "Lisa Patel"
    firm_users = state.get("firmUsers", [])
    lisa_patel_id = None
    for user in firm_users:
        if user.get("fullName") == "Lisa Patel":
            lisa_patel_id = user.get("id")
            break

    if lisa_patel_id is None:
        return False, "Firm user 'Lisa Patel' not found."

    # Find the template named "Criminal Defense - Misdemeanor"
    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        if tmpl.get("name") == "Criminal Defense - Misdemeanor":
            if tmpl.get("responsibleStaffId") != lisa_patel_id:
                return False, (
                    f"Template 'Criminal Defense - Misdemeanor' has responsibleStaffId "
                    f"'{tmpl.get('responsibleStaffId')}' but expected '{lisa_patel_id}' (Lisa Patel)."
                )
            return True, "Template 'Criminal Defense - Misdemeanor' has responsibleStaffId set to Lisa Patel."

    return False, "Template 'Criminal Defense - Misdemeanor' not found in matterTemplates."
