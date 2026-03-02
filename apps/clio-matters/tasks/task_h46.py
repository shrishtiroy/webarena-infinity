import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check numbering scheme
    ns = state.get("numberingScheme", {})
    if ns.get("separator") != "/":
        errors.append(f"Numbering separator is '{ns.get('separator')}', expected '/'.")
    if ns.get("numberPadding") != 4:
        errors.append(f"Numbering padding is {ns.get('numberPadding')}, expected 4.")

    # Check for Tax Law - Audit Defense template
    template = next(
        (t for t in state.get("matterTemplates", [])
         if "tax law" in t.get("name", "").lower()
         and "audit" in t.get("name", "").lower()),
        None
    )
    if template is None:
        errors.append("No 'Tax Law - Audit Defense' template found.")
    else:
        if template.get("practiceAreaId") != "pa_11":
            # Find Tax Law PA dynamically
            tax_pa = next(
                (pa for pa in state.get("practiceAreas", [])
                 if "tax" in pa.get("name", "").lower()),
                None
            )
            if tax_pa and template.get("practiceAreaId") != tax_pa["id"]:
                errors.append(
                    f"Template practice area is '{template.get('practiceAreaId')}', "
                    f"expected Tax Law ({tax_pa['id']})."
                )
        if template.get("billingMethod") != "hourly":
            errors.append(
                f"Template billing method is '{template.get('billingMethod')}', expected 'hourly'."
            )

    if errors:
        return False, "Settings changes not applied correctly. " + " | ".join(errors)

    return True, (
        "Matter numbering updated to slash separator with 4-digit padding, "
        "and Tax Law - Audit Defense template created with hourly billing."
    )
