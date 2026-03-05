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
         and ("bus" in m.get("description", "").lower()
              or "metro transit" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find Patterson bus accident matter."

    matter_id = matter["id"]

    # Check Bay Area Orthopedic Associates (contact_56) is a related contact
    relationships = matter.get("relationships", [])
    ortho_relationship = next(
        (r for r in relationships if r.get("contactId") == "contact_56"),
        None
    )

    if ortho_relationship is None:
        rel_contacts = [r.get("contactId") for r in relationships]
        errors.append(
            f"Bay Area Orthopedic Associates (contact_56) not found in relationships. "
            f"Current relationship contacts: {rel_contacts}."
        )
    else:
        rel_type = ortho_relationship.get("relationship", "")
        if "medical" not in rel_type.lower() and "provider" not in rel_type.lower():
            errors.append(
                f"Relationship type for Bay Area Orthopedic is '{rel_type}', "
                f"expected 'Medical Provider'."
            )

    # Check settlement has outstanding balance ~$2,500 to Bay Area Orthopedic
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})
    outstanding = settlement.get("outstandingBalances", [])

    has_balance = any(
        abs(float(ob.get("originalAmount", ob.get("balanceOwing", 0))) - 2500) < 500
        for ob in outstanding
    )
    if not has_balance:
        ob_amounts = [
            (ob.get("description"), ob.get("originalAmount", ob.get("balanceOwing")))
            for ob in outstanding
        ]
        errors.append(
            f"No outstanding balance with amount close to $2,500 found in settlement. "
            f"Existing balances: {ob_amounts}."
        )

    if errors:
        return False, "Patterson bus accident matter not updated correctly. " + " | ".join(errors)

    return True, (
        f"Patterson bus accident matter ({matter_id}) has Bay Area Orthopedic Associates "
        f"as Medical Provider relationship and $2,500 outstanding balance in settlement."
    )
