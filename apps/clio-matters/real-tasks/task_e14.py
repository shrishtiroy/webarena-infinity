import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez v. Premier Auto" in desc or matter_id == "mat_001":
            deduction_order = matter.get("deductionOrder", "")
            # Also check nested under billingPreference
            if not deduction_order:
                billing_pref = matter.get("billingPreference", {}) or {}
                deduction_order = billing_pref.get("deductionOrder", "")
            if deduction_order == "expenses_first":
                return True, "Rodriguez case deduction order is now expenses_first."
            else:
                return False, f"Rodriguez case deductionOrder is '{deduction_order}', expected 'expenses_first'."

    return False, "Could not find the Rodriguez v. Premier Auto matter in state."
