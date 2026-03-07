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

    # Check 1: Recovery for State Farm (con_023) with amount 50000
    sf_recovery = None
    for rec in recoveries:
        if rec.get("sourceContactId") == "con_023":
            sf_recovery = rec
            break

    if not sf_recovery:
        errors.append("No recovery found for State Farm Insurance (con_023)")
    else:
        if sf_recovery.get("amount") != 50000:
            errors.append(f"State Farm recovery amount is {sf_recovery.get('amount')}, expected 50000")

        # Check 2: Legal fee linked to that recovery with recipientId usr_003 and rate 33.33
        sf_rec_id = sf_recovery.get("id", "")
        lf_found = False
        for lf in legal_fees:
            if lf.get("recoveryId") == sf_rec_id:
                lf_found = True
                if lf.get("recipientId") != "usr_003":
                    errors.append(f"Legal fee recipientId is '{lf.get('recipientId')}', expected 'usr_003' (Maria Garcia)")
                if lf.get("rate") != 33.33:
                    errors.append(f"Legal fee rate is {lf.get('rate')}, expected 33.33")
                break

        if not lf_found:
            errors.append(f"No legal fee found linked to State Farm recovery (recoveryId={sf_rec_id})")

    if errors:
        return False, "; ".join(errors)

    return True, "State Farm $50,000 recovery added to Rodriguez with legal fee for Maria Garcia at 33.33%."
