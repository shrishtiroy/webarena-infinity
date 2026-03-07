import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Chicago Physical Therapy Center contact id
    contacts = state.get("contacts", [])
    cptc_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Chicago Physical Therapy" in name:
            cptc_id = contact.get("id", "")
            break
    if not cptc_id:
        cptc_id = "con_019"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            providers = matter.get("medicalProviders", [])
            for provider in providers:
                if provider.get("contactId") == cptc_id:
                    bills = provider.get("medicalBills", [])
                    for bill in bills:
                        if bill.get("fileName") == "CPTC_Additional_Bill.pdf":
                            amount = bill.get("billAmount", 0)
                            if amount == 3500:
                                return True, "Medical bill CPTC_Additional_Bill.pdf with $3,500 added to Chicago PT provider on Rodriguez."
                            else:
                                return False, f"Found CPTC_Additional_Bill.pdf but billAmount is {amount}, expected 3500."
                    return False, "No medical bill with fileName 'CPTC_Additional_Bill.pdf' found in Chicago PT provider on Rodriguez."
            return False, "No medical provider with Chicago Physical Therapy Center contactId found on Rodriguez."

    return False, "Could not find the Rodriguez matter in state."
