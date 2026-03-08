import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = None
    cruz = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
        elif "Cruz" in desc and "Metro Transit" in desc:
            cruz = m

    if not rodriguez:
        return False, "Rodriguez matter not found."
    if not cruz:
        return False, "Cruz matter not found."

    rod_bp = rodriguez.get("billingPreference", {})
    cruz_bp = cruz.get("billingPreference", {})

    errors = []

    expected_budget = rod_bp.get("budget")
    if cruz_bp.get("budget") != expected_budget:
        errors.append(f"Cruz budget is {cruz_bp.get('budget')}, expected {expected_budget}.")

    expected_trust_min = rod_bp.get("trustMinBalance")
    if cruz_bp.get("trustMinBalance") != expected_trust_min:
        errors.append(
            f"Cruz trustMinBalance is {cruz_bp.get('trustMinBalance')}, "
            f"expected {expected_trust_min}."
        )

    expected_notify = sorted(rod_bp.get("trustNotifyUsers", []))
    actual_notify = sorted(cruz_bp.get("trustNotifyUsers", []))
    if actual_notify != expected_notify:
        errors.append(
            f"Cruz trustNotifyUsers is {actual_notify}, expected {expected_notify}."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Cruz budget and trust settings updated to match Rodriguez."
