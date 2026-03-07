import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Lakeside Insurance Co. contact id
    contacts = state.get("contacts", [])
    lakeside_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Lakeside Insurance" in name:
            lakeside_id = contact.get("id", "")
            break
    if not lakeside_id:
        lakeside_id = "con_014"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            settlement = matter.get("settlement", {})
            recoveries = settlement.get("recoveries", [])
            for rec in recoveries:
                if rec.get("sourceContactId") == lakeside_id:
                    amount = rec.get("amount", 0)
                    if amount == 200000:
                        return True, "Lakeside Insurance recovery on Rodriguez updated to $200,000."
                    else:
                        return False, f"Found Lakeside Insurance recovery but amount is {amount}, expected 200000."
            return False, "No recovery from Lakeside Insurance found in Rodriguez settlement."

    return False, "Could not find the Rodriguez matter in state."
