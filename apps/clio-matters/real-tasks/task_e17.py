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
        if "Morales" in desc or matter_id == "mat_015":
            # Check billingMethod at top level first
            billing_method = matter.get("billingMethod", "")
            # Also check nested under billingPreference
            billing_pref = matter.get("billingPreference", {}) or {}
            nested_method = billing_pref.get("billingMethod", "")

            if billing_method == "flat_rate" or nested_method == "flat_rate":
                return True, "Morales assault case billing method is now flat_rate."
            else:
                actual = nested_method or billing_method
                return False, f"Morales assault case billingMethod is '{actual}', expected 'flat_rate'."

    return False, "Could not find the Morales assault matter in state."
