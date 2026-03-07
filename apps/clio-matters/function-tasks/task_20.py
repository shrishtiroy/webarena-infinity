import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Lakeside Insurance Co. contact by lastName
    contacts = state.get("contacts", [])
    lakeside_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Lakeside Insurance Co."),
        None
    )
    if not lakeside_contact:
        return False, "Contact 'Lakeside Insurance Co.' (company) not found in contacts."

    lakeside_id = lakeside_contact["id"]
    recoveries = matter.get("settlement", {}).get("recoveries", [])
    match = next(
        (r for r in recoveries
         if r.get("sourceContactId") == lakeside_id and r.get("amount") == 200000),
        None
    )
    if not match:
        lakeside_recoveries = [r for r in recoveries if r.get("sourceContactId") == lakeside_id]
        if lakeside_recoveries:
            return False, (
                f"Found recovery from Lakeside Insurance Co. but amount is "
                f"{lakeside_recoveries[0].get('amount')}, expected 200000."
            )
        return False, "No recovery found from Lakeside Insurance Co."

    return True, "Recovery from Lakeside Insurance Co. with amount 200000 found."
