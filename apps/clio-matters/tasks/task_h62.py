import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Patterson bus accident matter
    matter = next(
        (m for m in state.get("matters", [])
         if "patterson" in m.get("description", "").lower()
         and "metro transit" in m.get("description", "").lower()),
        None,
    )
    if matter is None:
        return False, "Patterson bus accident matter not found."

    matter_id = matter["id"]

    # Calculate total outstanding balance from medical bills
    bills = [b for b in state.get("medicalBills", []) if b.get("matterId") == matter_id]
    total_balance = sum(float(b.get("balanceOwed", 0)) for b in bills)

    if total_balance <= 0:
        return False, f"No medical bill balances found for {matter_id}."

    # Check settlement has a non-medical lien matching that total from State Farm
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})

    if not settlement:
        return False, f"No settlement found for Patterson bus accident matter ({matter_id})."

    liens = settlement.get("nonMedicalLiens", [])
    # Look for a lien within $500 tolerance of the computed total
    has_matching_lien = any(
        abs(float(lien.get("amount", 0)) - total_balance) < 500
        for lien in liens
    )

    if not has_matching_lien:
        lien_amounts = [lien.get("amount") for lien in liens]
        errors.append(
            f"No non-medical lien matching medical bill total (${total_balance:,.0f}) found. "
            f"Lien amounts: {lien_amounts}."
        )

    # Verify the lien is from State Farm
    state_farm_lien = any(
        abs(float(lien.get("amount", 0)) - total_balance) < 500
        and (lien.get("holderContactId") == "contact_58"
             or "state farm" in lien.get("description", "").lower())
        for lien in liens
    )
    if not state_farm_lien and not errors:
        errors.append("Lien with correct amount exists but is not from State Farm Insurance.")

    if errors:
        return False, (
            f"Patterson bus accident settlement lien not correct. "
            f"Expected lien of ${total_balance:,.0f} from State Farm. "
            + " | ".join(errors)
        )

    return True, (
        f"Non-medical lien of ${total_balance:,.0f} from State Farm Insurance correctly added "
        f"to Patterson bus accident settlement, matching total medical bill balances."
    )
