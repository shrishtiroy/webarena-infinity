import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00004":
            matter = m
            break

    if matter is None:
        return False, "Matter '00004' (Washington) not found."

    billing = matter.get("billing", {})
    minimum_trust = billing.get("minimumTrust")

    if minimum_trust is None:
        return False, f"Matter '00004' has no minimumTrust set. Billing: {billing}"

    if minimum_trust != 5000:
        return False, f"Matter '00004' minimumTrust is {minimum_trust}, expected 5000."

    return True, "Matter '00004' (Washington) minimumTrust is correctly set to 5000."
