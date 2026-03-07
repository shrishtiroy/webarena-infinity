import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Rodriguez v. Premier Auto" in desc:
            deduction_order = matter.get("deductionOrder", "")
            if deduction_order == "expenses_first":
                return True, f"Matter '{desc}' has deductionOrder 'expenses_first' as expected."
            else:
                return False, f"Matter '{desc}' has deductionOrder '{deduction_order}', expected 'expenses_first'."

    return False, "No matter found with description containing 'Rodriguez v. Premier Auto'."
