import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    templates = state.get("matterTemplates", [])

    # Check old template is deleted
    old_exists = any(
        t.get("name") == "Family Law - Divorce"
        for t in templates
    )
    if old_exists:
        errors.append("'Family Law - Divorce' template still exists (should be deleted).")

    # Check new template exists
    new_template = next(
        (t for t in templates
         if "dissolution" in t.get("name", "").lower()
         and "family" in t.get("name", "").lower()),
        None
    )
    if new_template is None:
        errors.append("No 'Family Law - Dissolution' template found.")
    else:
        # Check it's linked to Family Law (pa_2)
        if new_template.get("practiceAreaId") != "pa_2":
            errors.append(
                f"New template practice area is '{new_template.get('practiceAreaId')}', "
                f"expected 'pa_2' (Family Law)."
            )
        # Check billing method is hourly
        if new_template.get("billingMethod") != "hourly":
            errors.append(
                f"New template billing method is '{new_template.get('billingMethod')}', "
                f"expected 'hourly'."
            )
        # Check it's set as firm default
        firm_default = state.get("firmSettings", {}).get("defaultTemplateId")
        if firm_default != new_template.get("id"):
            errors.append(
                f"Firm default template is '{firm_default}', expected '{new_template.get('id')}' "
                f"(the new Family Law - Dissolution template)."
            )

    if errors:
        return False, "Template changes not applied correctly. " + " | ".join(errors)

    return True, (
        "Family Law - Divorce template deleted, "
        "Family Law - Dissolution created with hourly billing for Family Law, "
        "and set as firm default."
    )
