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
    recoveries = settlement.get("recoveries", [])
    legal_fees = settlement.get("legalFees", [])

    errors = []

    # Check 1: No recovery with sourceContactId == con_015 (Premier Auto)
    for rec in recoveries:
        if rec.get("sourceContactId") == "con_015":
            errors.append("Recovery for Premier Auto Dealers (con_015) still exists; should have been removed")
            break

    # Check 2: No legal fees linked to the deleted recovery (rec_002)
    # We check that no legal fee references rec_002 or any Premier Auto recovery
    premier_rec_ids = set()
    for rec in recoveries:
        if rec.get("sourceContactId") == "con_015":
            premier_rec_ids.add(rec.get("id", ""))
    # Also check for the original rec_002
    for lf in legal_fees:
        rec_id = lf.get("recoveryId", "")
        if rec_id == "rec_002" or rec_id in premier_rec_ids:
            errors.append(f"Legal fee still linked to Premier Auto recovery (recoveryId={rec_id})")
            break

    # Check 3: Lakeside (con_014) recovery amount == 250000
    lakeside_found = False
    for rec in recoveries:
        if rec.get("sourceContactId") == "con_014":
            lakeside_found = True
            amt = rec.get("amount", 0)
            if amt != 250000:
                errors.append(f"Lakeside recovery amount is {amt}, expected 250000")
            break

    if not lakeside_found:
        errors.append("No recovery found for Lakeside Insurance (con_014)")

    if errors:
        return False, "; ".join(errors)

    return True, "Premier Auto recovery removed, associated legal fee removed, Lakeside recovery increased to $250,000."
