import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the Gonzalez divorce matter (not paternity, not DoorDash, not surgical)
    gonzalez_divorce = next(
        (m for m in state.get("matters", [])
         if "gonzalez" in m.get("description", "").lower()
         and "divorce" in m.get("description", "").lower()),
        None
    )
    if gonzalez_divorce is None:
        return False, "Could not find the Gonzalez divorce matter."

    matter_id = gonzalez_divorce["id"]

    # Verify it's NOT the paternity matter
    if "paternity" in gonzalez_divorce.get("description", "").lower():
        return False, "Found the paternity matter instead of the divorce matter."

    # Check settlement
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})

    if not settlement:
        return False, f"No settlement found for Gonzalez divorce ({matter_id})."

    # Recovery ~$175,000
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 175000) < 15000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$175,000 found. Recovery amounts: {amounts}.")

    # Legal fee ~25%
    legal_fees = settlement.get("legalFees", [])
    has_fee = any(
        abs(float(lf.get("percentage", lf.get("rate", 0))) - 25) < 3
        for lf in legal_fees
    )
    if not has_fee:
        pcts = [lf.get("percentage", lf.get("rate")) for lf in legal_fees]
        errors.append(f"No legal fee ~25% found. Fee percentages: {pcts}.")

    # Non-medical lien ~$12,000 for child support
    liens = settlement.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 12000) < 2000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(f"No non-medical lien ~$12,000 found. Lien amounts: {lien_amounts}.")

    if errors:
        return False, "Gonzalez divorce settlement not set up correctly. " + " | ".join(errors)

    return True, (
        f"Gonzalez divorce settlement ({matter_id}) correctly set up: "
        f"~$175,000 recovery, ~25% legal fee, ~$12,000 child support lien."
    )
