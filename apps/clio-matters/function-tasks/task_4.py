import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        desc = m.get("description", "")
        if "Garcia v. Bay Area Taxi" in desc:
            matter = m
            break

    if matter is None:
        return False, "Could not find a matter with description containing 'Garcia v. Bay Area Taxi'."

    errors = []

    if matter.get("clientId") != "contact_1":
        errors.append(f"Expected clientId 'contact_1' (James Patterson), but got '{matter.get('clientId')}'.")

    if matter.get("responsibleAttorneyId") != "user_2":
        errors.append(f"Expected responsibleAttorneyId 'user_2' (Marcus Williams), but got '{matter.get('responsibleAttorneyId')}'.")

    if matter.get("practiceAreaId") != "pa_1":
        errors.append(f"Expected practiceAreaId 'pa_1' (Personal Injury), but got '{matter.get('practiceAreaId')}'.")

    billing_method = matter.get("billingMethod", "")
    billing_obj_method = matter.get("billing", {}).get("method", "")
    if billing_method != "contingency" and billing_obj_method != "contingency":
        errors.append(f"Expected billingMethod or billing.method to be 'contingency', but got billingMethod='{billing_method}', billing.method='{billing_obj_method}'.")

    if errors:
        return False, "New matter 'Garcia v. Bay Area Taxi' found but has issues: " + " ".join(errors)

    return True, "New matter 'Garcia v. Bay Area Taxi' exists with correct client, attorney, practice area, and billing method."
