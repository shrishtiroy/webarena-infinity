import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check for Medical Malpractice - Standard template
    templates = state.get("matterTemplates", [])
    mm_template = next(
        (t for t in templates
         if "medical malpractice" in t.get("name", "").lower()
         and "standard" in t.get("name", "").lower()),
        None
    )

    if mm_template is None:
        template_names = [t.get("name") for t in templates]
        return False, (
            f"Medical Malpractice - Standard template not found. "
            f"Templates: {template_names}."
        )

    template_id = mm_template["id"]

    # Check billing method is contingency
    if mm_template.get("billingMethod") != "contingency":
        errors.append(
            f"Template billing method is '{mm_template.get('billingMethod')}', "
            f"expected 'contingency'."
        )

    # Check practice area is Medical Malpractice (pa_12)
    if mm_template.get("practiceAreaId") != "pa_12":
        errors.append(
            f"Template practice area is '{mm_template.get('practiceAreaId')}', "
            f"expected 'pa_12' (Medical Malpractice)."
        )

    # Check it's set as the firm default
    firm_settings = state.get("firmSettings", {})
    default_template_id = firm_settings.get("defaultTemplateId")

    if default_template_id != template_id:
        errors.append(
            f"Firm default template is '{default_template_id}', "
            f"expected '{template_id}' (Medical Malpractice - Standard)."
        )

    if errors:
        return False, "Medical Malpractice template setup not complete. " + " | ".join(errors)

    return True, (
        f"Medical Malpractice - Standard template ({template_id}) created with "
        f"contingency billing, Medical Malpractice practice area, and set as firm default."
    )
