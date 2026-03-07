import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Singh Family Trust" in desc or matter_id == "mat_007":
            billing = matter.get("billingPreference", {})
            method = billing.get("billingMethod", "")
            currency = billing.get("currency", "")
            errors = []
            if method != "hourly":
                errors.append(f"billingMethod is '{method}', expected 'hourly'")
            if currency != "CAD":
                errors.append(f"currency is '{currency}', expected 'CAD'")
            if errors:
                return False, f"Singh Family Trust matter found but: {'; '.join(errors)}."
            return True, "Singh Family Trust billing updated to hourly with CAD currency."

    return False, "Could not find the Singh Family Trust matter in state."
