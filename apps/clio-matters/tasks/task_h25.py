import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the Chen-Ramirez criminal matter at Arraignment (stage_3_1)
    # There are two: matter_43 (DUI, stage_3_2) and matter_51 (Reckless driving, stage_3_1)
    chen_matters = [
        m for m in state.get("matters", [])
        if "chen-ramirez" in m.get("description", "").lower()
        and m.get("practiceAreaId") == "pa_3"
    ]

    arraignment_matter = next(
        (m for m in chen_matters if m.get("stageId") == "stage_3_1"),
        None
    )

    # If no matter is at Arraignment anymore, find matter_51 by ID
    if arraignment_matter is None:
        arraignment_matter = next(
            (m for m in state.get("matters", []) if m.get("id") == "matter_51"),
            None
        )

    if arraignment_matter is None:
        return False, "Could not find Chen-Ramirez criminal matter at Arraignment stage (matter_51)."

    matter_id = arraignment_matter["id"]

    # Check billing method changed to hourly
    billing_method = arraignment_matter.get("billingMethod")
    billing_obj = arraignment_matter.get("billing", {})
    billing_method_obj = billing_obj.get("method")

    if billing_method != "hourly" and billing_method_obj != "hourly":
        errors.append(
            f"Billing method is '{billing_method}' / '{billing_method_obj}', expected 'hourly'."
        )

    # Check budget is $15,000
    budget = billing_obj.get("budget", 0)
    if abs(float(budget) - 15000) > 1000:
        errors.append(
            f"Budget is ${budget:,.0f}, expected ~$15,000."
        )

    if errors:
        return False, (
            f"Chen-Ramirez Arraignment matter ({matter_id}) not updated correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"Chen-Ramirez matter at Arraignment ({matter_id}) billing changed to hourly "
        f"with budget ~$15,000."
    )
