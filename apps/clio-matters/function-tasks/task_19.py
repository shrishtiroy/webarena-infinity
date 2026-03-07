import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find State Farm Insurance contact by lastName
    contacts = state.get("contacts", [])
    sf_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "State Farm Insurance"),
        None
    )
    if not sf_contact:
        return False, "Contact 'State Farm Insurance' (company) not found in contacts."

    sf_id = sf_contact["id"]
    recoveries = matter.get("settlement", {}).get("recoveries", [])
    match = next(
        (r for r in recoveries
         if r.get("sourceContactId") == sf_id and r.get("amount") == 50000),
        None
    )
    if not match:
        sf_recoveries = [r for r in recoveries if r.get("sourceContactId") == sf_id]
        if sf_recoveries:
            return False, (
                f"Found recovery from State Farm Insurance but amount is {sf_recoveries[0].get('amount')}, expected 50000."
            )
        return False, "No recovery found from State Farm Insurance."

    return True, "Recovery from State Farm Insurance with amount 50000 found."
