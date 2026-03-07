import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "State v. Morales" in desc:
            billing_pref = matter.get("billingPreference", {})
            billing_method = billing_pref.get("billingMethod", "")
            if billing_method == "flat_rate":
                return True, f"Matter '{desc}' has billingPreference.billingMethod 'flat_rate' as expected."
            else:
                return False, f"Matter '{desc}' has billingPreference.billingMethod '{billing_method}', expected 'flat_rate'."

    return False, "No matter found with description containing 'State v. Morales'."
