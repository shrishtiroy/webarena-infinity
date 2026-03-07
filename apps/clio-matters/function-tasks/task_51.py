import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the practice area named "Immigration" to get its ID
    practice_areas = state.get("practiceAreas", [])
    immigration_pa_id = None
    for pa in practice_areas:
        if pa.get("name") == "Immigration":
            immigration_pa_id = pa.get("id")
            break

    if immigration_pa_id is None:
        return False, "Practice area 'Immigration' not found."

    # Find the template named "Immigration - Work Visa"
    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        if tmpl.get("name") == "Immigration - Work Visa":
            if tmpl.get("practiceAreaId") != immigration_pa_id:
                return False, (
                    f"Template 'Immigration - Work Visa' has practiceAreaId "
                    f"'{tmpl.get('practiceAreaId')}' but expected '{immigration_pa_id}'."
                )
            if tmpl.get("billingMethod") != "hourly":
                return False, (
                    f"Template 'Immigration - Work Visa' has billingMethod "
                    f"'{tmpl.get('billingMethod')}' but expected 'hourly'."
                )
            return True, "Template 'Immigration - Work Visa' found with correct practiceAreaId and billingMethod 'hourly'."

    return False, "Template 'Immigration - Work Visa' not found in matterTemplates."
