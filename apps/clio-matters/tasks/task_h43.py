import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the renamed template (was "Personal Injury - Auto Accident")
    template = next(
        (t for t in state.get("matterTemplates", [])
         if "motor vehicle" in t.get("name", "").lower()
         and "collision" in t.get("name", "").lower()),
        None
    )
    old_template = next(
        (t for t in state.get("matterTemplates", [])
         if t.get("name") == "Personal Injury - Auto Accident"),
        None
    )

    if template is None:
        if old_template:
            errors.append(
                "Template still named 'Personal Injury - Auto Accident'. "
                "Expected rename to 'Personal Injury - Motor Vehicle Collision'."
            )
        else:
            errors.append("Could not find the renamed template (expected 'Personal Injury - Motor Vehicle Collision').")
    else:
        template_id = template["id"]

        # Check billing method changed to hourly
        if template.get("billingMethod") != "hourly":
            errors.append(
                f"Template billing method is '{template.get('billingMethod')}', expected 'hourly'."
            )

        # Check it's set as the firm's default
        firm_default = state.get("firmSettings", {}).get("defaultTemplateId")
        if firm_default != template_id:
            errors.append(
                f"Firm default template is '{firm_default}', expected '{template_id}' "
                f"(the renamed Motor Vehicle Collision template)."
            )

    if errors:
        return False, "Template changes not applied correctly. " + " | ".join(errors)

    return True, (
        "Template correctly renamed to 'Personal Injury - Motor Vehicle Collision', "
        "billing changed to hourly, and set as firm default."
    )
