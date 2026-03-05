import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Chen-Ramirez Amazon delivery truck case
    matter = next(
        (m for m in state.get("matters", [])
         if "chen-ramirez" in m.get("description", "").lower()
         and "amazon" in m.get("description", "").lower()),
        None,
    )
    if matter is None:
        return False, "Chen-Ramirez Amazon delivery truck case not found."

    matter_id = matter["id"]

    # Check deduction order
    pi = matter.get("personalInjury") or {}
    if pi.get("deductionOrder") != "expenses_first":
        errors.append(
            f"Deduction order is '{pi.get('deductionOrder')}', expected 'expenses_first'."
        )

    # Check settlement
    settlement = state.get("settlements", {}).get(matter_id, {})
    if not settlement:
        return False, f"No settlement found for Chen-Ramirez Amazon case ({matter_id})."

    # Recovery ~$180,000
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 180000) < 18000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$180,000 found. Amounts: {amounts}.")

    # Legal fee ~33.33%
    fees = settlement.get("legalFees", [])
    has_fee = any(
        abs(float(f.get("percentage", f.get("rate", 0))) - 33.33) < 2
        for f in fees
    )
    if not has_fee:
        pcts = [f.get("percentage", f.get("rate")) for f in fees]
        errors.append(f"No legal fee ~33.33% found. Percentages: {pcts}.")

    # Non-medical lien ~$12,000 from ABC Insurance
    liens = settlement.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 12000) < 2000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(f"No non-medical lien ~$12,000 found. Amounts: {lien_amounts}.")

    # Outstanding balance ~$4,500 owed to SF General
    balances = settlement.get("outstandingBalances", [])
    has_balance = any(
        abs(float(b.get("balanceOwing", b.get("originalAmount", 0))) - 4500) < 1000
        for b in balances
    )
    if not has_balance:
        bal_amounts = [b.get("balanceOwing", b.get("originalAmount")) for b in balances]
        errors.append(f"No outstanding balance ~$4,500 found. Amounts: {bal_amounts}.")

    if errors:
        return False, (
            "Chen-Ramirez Amazon settlement not set up completely. " + " | ".join(errors)
        )

    return True, (
        "Chen-Ramirez Amazon delivery case settlement fully configured: "
        "$180,000 recovery, 33.33% fee, $12,000 lien, $4,500 balance, "
        "deduction order expenses first."
    )
