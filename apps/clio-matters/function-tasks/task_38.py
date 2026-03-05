import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    matching = [t for t in templates if t.get("name") == "Immigration - Work Visa"]
    if not matching:
        return False, "Template 'Immigration - Work Visa' not found in matterTemplates."

    template = matching[0]

    if template.get("practiceAreaId") != "pa_8":
        return False, f"Expected practiceAreaId 'pa_8', got '{template.get('practiceAreaId')}'."

    if template.get("billingMethod") != "hourly":
        return False, f"Expected billingMethod 'hourly', got '{template.get('billingMethod')}'."

    return True, "Template 'Immigration - Work Visa' exists with practiceAreaId 'pa_8' and billingMethod 'hourly'."
