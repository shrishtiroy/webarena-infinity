import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Immigration practice area id
    practice_areas = state.get("practiceAreas", [])
    immigration_id = None
    for pa in practice_areas:
        if pa.get("name") == "Immigration":
            immigration_id = pa.get("id", "")
            break
    if not immigration_id:
        immigration_id = "pa_007"

    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        name = tmpl.get("name", "") or ""
        if name == "Immigration - Work Visa":
            pa_id = tmpl.get("practiceAreaId", "")
            billing = tmpl.get("billingMethod", "")
            errors = []
            if pa_id != immigration_id:
                errors.append(f"practiceAreaId is '{pa_id}', expected '{immigration_id}'")
            if billing != "hourly":
                errors.append(f"billingMethod is '{billing}', expected 'hourly'")
            if errors:
                return False, f"Found 'Immigration - Work Visa' template but: {'; '.join(errors)}."
            return True, "Immigration - Work Visa template created for Immigration practice area with hourly billing."

    return False, "Could not find a template named 'Immigration - Work Visa' in matterTemplates."
