import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Doyle scaffolding fall matter (matter_5)
    matter = next(
        (m for m in state.get("matters", [])
         if "doyle" in m.get("description", "").lower()
         and ("scaffolding" in m.get("description", "").lower()
              or "summit" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find Doyle scaffolding fall matter."

    matter_id = matter["id"]

    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})

    if not settlement:
        return False, f"No settlement found for Doyle scaffolding matter ({matter_id})."

    # Check recovery ~$350,000
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 350000) < 15000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$350,000 found. Recovery amounts: {amounts}.")

    # Check legal fee ~33.33%
    legal_fees = settlement.get("legalFees", [])
    has_fee = any(
        abs(float(lf.get("percentage", lf.get("rate", 0))) - 33.33) < 2
        for lf in legal_fees
    )
    if not has_fee:
        pcts = [lf.get("percentage", lf.get("rate")) for lf in legal_fees]
        errors.append(f"No legal fee ~33.33% found. Fee percentages: {pcts}.")

    # Check non-medical lien ~$15,000
    liens = settlement.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 15000) < 3000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(f"No non-medical lien ~$15,000 found. Lien amounts: {lien_amounts}.")

    # Check outstanding balance ~$8,500
    outstanding = settlement.get("outstandingBalances", [])
    has_balance = any(
        abs(float(ob.get("originalAmount", ob.get("balanceOwing", 0))) - 8500) < 1500
        for ob in outstanding
    )
    if not has_balance:
        ob_amounts = [ob.get("originalAmount", ob.get("balanceOwing")) for ob in outstanding]
        errors.append(f"No outstanding balance ~$8,500 found. Balance amounts: {ob_amounts}.")

    if errors:
        return False, "Doyle scaffolding settlement not set up correctly. " + " | ".join(errors)

    return True, (
        f"Doyle scaffolding fall settlement ({matter_id}) correctly configured: "
        f"~$350,000 recovery, ~33.33% legal fee, ~$15,000 lien, ~$8,500 outstanding balance."
    )
