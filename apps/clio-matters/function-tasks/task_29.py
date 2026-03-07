import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Riverside Community Credit Union contact
    contacts = state.get("contacts", [])
    rccu_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Riverside Community Credit Union"),
        None
    )
    if not rccu_contact:
        return False, "Contact 'Riverside Community Credit Union' (company) not found in contacts."

    rccu_id = rccu_contact["id"]
    outstanding_balances = matter.get("settlement", {}).get("outstandingBalances", [])
    match = next(
        (ob for ob in outstanding_balances
         if ob.get("balanceHolderId") == rccu_id
         and ob.get("reduction") == 500),
        None
    )
    if not match:
        rccu_balances = [ob for ob in outstanding_balances if ob.get("balanceHolderId") == rccu_id]
        if rccu_balances:
            reductions = [ob.get("reduction") for ob in rccu_balances]
            return False, (
                f"Found outstanding balance(s) from Riverside Community Credit Union but "
                f"reduction is {reductions}, expected 500."
            )
        return False, "No outstanding balance found from Riverside Community Credit Union."

    return True, "Outstanding balance from Riverside Community Credit Union with reduction 500 found."
