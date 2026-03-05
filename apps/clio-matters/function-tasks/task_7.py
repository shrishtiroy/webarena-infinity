import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00006":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00006'."

    billing_method = matter.get("billingMethod", "")
    billing_obj_method = matter.get("billing", {}).get("method", "")
    if billing_method != "hourly" and billing_obj_method != "hourly":
        return False, f"Expected matter '00006-McCarthy' billingMethod to be 'hourly', but got billingMethod='{billing_method}', billing.method='{billing_obj_method}'."

    return True, "Matter '00006-McCarthy' billingMethod is correctly set to 'hourly'."
