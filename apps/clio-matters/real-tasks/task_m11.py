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
            # Find the Lakeside recovery id
            lakeside_recovery_id = None
            for rec in recoveries:
                if rec.get("sourceContactId") == lakeside_id:
                    lakeside_recovery_id = rec.get("id", "")
                    break
            if not lakeside_recovery_id:
                return False, "No recovery from Lakeside Insurance found in Rodriguez settlement."

            legal_fees = settlement.get("legalFees", [])
            for lf in legal_fees:
                if lf.get("recoveryId") == lakeside_recovery_id:
                    discount = lf.get("discount", 0)
                    if discount == 15:
                        return True, "Legal fee discount set to 15% on Lakeside Insurance recovery in Rodriguez."
                    else:
                        return False, f"Found legal fee for Lakeside recovery but discount is {discount}, expected 15."
            return False, "No legal fee entry found for Lakeside Insurance recovery in Rodriguez settlement."

    return False, "Could not find the Rodriguez matter in state."
