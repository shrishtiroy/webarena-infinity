import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Sullivan-Wright surgical error case (matter_14)
    matter = next(
        (m for m in state.get("matters", [])
         if "sullivan" in m.get("description", "").lower()
         and ("wright" in m.get("description", "").lower()
              or "kaiser" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find Sullivan-Wright surgical error matter."

    matter_id = matter["id"]

    # Check deduction order is expenses_first
    pi = matter.get("personalInjury") or {}
    if pi.get("deductionOrder") != "expenses_first":
        errors.append(
            f"Deduction order is '{pi.get('deductionOrder')}', expected 'expenses_first'."
        )

    # Check settlement
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})

    if not settlement:
        return False, f"No settlement found for Sullivan-Wright matter ({matter_id})."

    # Recovery ~$450,000
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 450000) < 20000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$450,000 found. Recovery amounts: {amounts}.")

    # Legal fee ~40%
    legal_fees = settlement.get("legalFees", [])
    has_fee = any(
        abs(float(lf.get("percentage", lf.get("rate", 0))) - 40) < 2
        for lf in legal_fees
    )
    if not has_fee:
        pcts = [lf.get("percentage", lf.get("rate")) for lf in legal_fees]
        errors.append(f"No legal fee ~40% found. Fee percentages: {pcts}.")

    # Non-medical lien ~$35,000
    liens = settlement.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 35000) < 5000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(f"No non-medical lien ~$35,000 found. Lien amounts: {lien_amounts}.")

    # Outstanding balance ~$12,000
    outstanding = settlement.get("outstandingBalances", [])
    has_balance = any(
        abs(float(ob.get("originalAmount", ob.get("balanceOwing", 0))) - 12000) < 2000
        for ob in outstanding
    )
    if not has_balance:
        ob_amounts = [ob.get("originalAmount", ob.get("balanceOwing")) for ob in outstanding]
        errors.append(f"No outstanding balance ~$12,000 found. Balance amounts: {ob_amounts}.")

    if errors:
        return False, "Sullivan-Wright settlement not set up correctly. " + " | ".join(errors)

    return True, (
        f"Sullivan-Wright settlement ({matter_id}) correctly configured: "
        f"~$450,000 recovery, ~40% legal fee, ~$35,000 lien, ~$12,000 outstanding balance, "
        f"deduction order expenses_first."
    )
