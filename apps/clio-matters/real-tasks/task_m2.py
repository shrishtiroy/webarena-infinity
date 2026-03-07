import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find State Farm Insurance contact id
    contacts = state.get("contacts", [])
    state_farm_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "State Farm" in name:
            state_farm_id = contact.get("id", "")
            break
    if not state_farm_id:
        state_farm_id = "con_023"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            settlement = matter.get("settlement", {})
            recoveries = settlement.get("recoveries", [])
            for rec in recoveries:
                if rec.get("sourceContactId") == state_farm_id:
                    amount = rec.get("amount", 0)
                    if amount == 50000:
                        return True, "Recovery of $50,000 from State Farm Insurance added to Rodriguez settlement."
                    else:
                        return False, f"Found State Farm recovery but amount is {amount}, expected 50000."
            return False, "No recovery from State Farm Insurance found in Rodriguez settlement."

    return False, "Could not find the Rodriguez matter in state."
