import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Northwestern Memorial Hospital contact id
    contacts = state.get("contacts", [])
    nm_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Northwestern Memorial" in name:
            nm_id = contact.get("id", "")
            break
    if not nm_id:
        nm_id = "con_018"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            providers = matter.get("medicalProviders", [])
            for provider in providers:
                if provider.get("contactId") == nm_id:
                    bills = provider.get("medicalBills", [])
                    for bill in bills:
                        if bill.get("fileName") == "NM_Hospital_Bill.pdf":
                            adjustment = bill.get("adjustment", 0)
                            if adjustment == 7000:
                                return True, "NM_Hospital_Bill.pdf adjustment updated to $7,000 on Rodriguez."
                            else:
                                return False, f"Found NM_Hospital_Bill.pdf but adjustment is {adjustment}, expected 7000."
                    return False, "No bill with fileName 'NM_Hospital_Bill.pdf' found in NM Hospital provider on Rodriguez."
            return False, "No medical provider with Northwestern Memorial Hospital contactId found on Rodriguez."

    return False, "Could not find the Rodriguez matter in state."
