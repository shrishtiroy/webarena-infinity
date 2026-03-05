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

    personal_injury = matter.get("personalInjury", {})
    deduction_order = personal_injury.get("deductionOrder")

    if deduction_order is None:
        return False, f"Matter '00004' has no deductionOrder set. personalInjury: {personal_injury}"

    if deduction_order != "fees_first":
        return False, f"Matter '00004' deductionOrder is '{deduction_order}', expected 'fees_first'."

    return True, "Matter '00004' (Washington) deductionOrder is correctly set to 'fees_first'."
