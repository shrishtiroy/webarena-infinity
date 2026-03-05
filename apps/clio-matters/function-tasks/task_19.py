import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00001":
            matter = m
            break

    if matter is None:
        return False, "Matter '00001' (Patterson) not found."

    billing = matter.get("billing", {})
    budget = billing.get("budget")

    if budget is None:
        return False, f"Matter '00001' has no budget set. Billing: {billing}"

    if budget != 75000:
        return False, f"Matter '00001' budget is {budget}, expected 75000."

    return True, "Matter '00001' (Patterson) budget is correctly set to 75000."
