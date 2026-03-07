import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find State Farm Insurance contact
    contacts = state.get("contacts", [])
    sf_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "State Farm Insurance"),
        None
    )
    if not sf_contact:
        return False, "Contact 'State Farm Insurance' (company) not found in contacts."

    sf_id = sf_contact["id"]
    outstanding_balances = matter.get("settlement", {}).get("outstandingBalances", [])
    match = next(
        (ob for ob in outstanding_balances
         if ob.get("balanceHolderId") == sf_id
         and ob.get("responsibleParty") == "other"
         and ob.get("description") == "Overpayment recovery"
         and ob.get("balanceOwing") == 1500),
        None
    )
    if not match:
        sf_balances = [ob for ob in outstanding_balances if ob.get("balanceHolderId") == sf_id]
        if sf_balances:
            return False, (
                f"Found outstanding balance(s) from State Farm Insurance but none match expected values. "
                f"Found: {sf_balances}"
            )
        return False, "No outstanding balance found from State Farm Insurance."

    return True, (
        "Outstanding balance from State Farm Insurance with responsibleParty 'other', "
        "description 'Overpayment recovery', and balanceOwing 1500 found."
    )
