import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00007":
            matter = m
            break

    if matter is None:
        return False, "Matter '00007' (Okafor) not found."

    billing = matter.get("billing", {})
    contingency_fee = billing.get("contingencyFee", {})
    percentage = contingency_fee.get("percentage")

    if percentage is None:
        return False, f"Matter '00007' has no contingencyFee percentage set. Billing: {billing}"

    if percentage != 33.33:
        return False, f"Matter '00007' contingencyFee percentage is {percentage}, expected 33.33."

    return True, "Matter '00007' (Okafor) contingencyFee percentage is correctly set to 33.33."
