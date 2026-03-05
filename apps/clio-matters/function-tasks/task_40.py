import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])

    criminal = [t for t in templates if t.get("name") == "Criminal Defense - Misdemeanor"]
    if not criminal:
        return False, "Template 'Criminal Defense - Misdemeanor' not found in matterTemplates."

    if not criminal[0].get("isDefault"):
        return False, "Template 'Criminal Defense - Misdemeanor' is not set as default."

    pi_auto = [t for t in templates if t.get("name") == "Personal Injury - Auto Accident"]
    if pi_auto and pi_auto[0].get("isDefault"):
        return False, "Template 'Personal Injury - Auto Accident' is still set as default but should no longer be."

    return True, "Template 'Criminal Defense - Misdemeanor' is now the default template and 'Personal Injury - Auto Accident' is no longer default."
