import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Rodriguez matter
    rodriguez = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Rodriguez" in desc or mid == "mat_001":
            rodriguez = matter
            break

    if not rodriguez:
        return False, "Could not find the Rodriguez matter in state."

    settlement = rodriguez.get("settlement", {})
    other_liens = settlement.get("otherLiens", [])
    outstanding_balances = settlement.get("outstandingBalances", [])

    errors = []

    # Check 1: No lien with lienHolderId == con_028 (Riverside CU)
    for lien in other_liens:
        if lien.get("lienHolderId") == "con_028":
            errors.append("Riverside Community Credit Union lien (con_028) still exists in otherLiens")
            break

    # Check 2: No outstanding balance with balanceHolderId == con_028
    for ob in outstanding_balances:
        if ob.get("balanceHolderId") == "con_028":
            errors.append("Riverside Community Credit Union outstanding balance (con_028) still exists in outstandingBalances")
            break

    if errors:
        return False, "; ".join(errors)

    return True, "Riverside CU lien and outstanding balance both removed from Rodriguez settlement."
