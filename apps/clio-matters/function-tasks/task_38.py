import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Chicago Physical Therapy Center"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Chicago Physical Therapy Center"), None)
    if not contact:
        return False, "Contact 'Chicago Physical Therapy Center' not found."

    # Find matter "Rodriguez v. Premier Auto"
    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find provider
    provider = next(
        (p for p in matter.get("medicalProviders", []) if p["contactId"] == contact["id"]),
        None
    )
    if not provider:
        return False, "No medical provider with contactId for 'Chicago Physical Therapy Center' found on matter 'Rodriguez v. Premier Auto'."

    # Find medical bill with fileName "CPTC_Follow_Up_Bill.pdf"
    bill = next(
        (b for b in provider.get("medicalBills", []) if b.get("fileName") == "CPTC_Follow_Up_Bill.pdf"),
        None
    )
    if not bill:
        existing = [b.get("fileName") for b in provider.get("medicalBills", [])]
        return False, f"No medical bill with fileName 'CPTC_Follow_Up_Bill.pdf' found. Existing bills: {existing}"

    bill_amount = bill.get("billAmount")
    if bill_amount != 3500:
        return False, f"Medical bill 'CPTC_Follow_Up_Bill.pdf' has billAmount {bill_amount}, expected 3500."

    return True, "Provider 'Chicago Physical Therapy Center' on matter 'Rodriguez v. Premier Auto' has medical bill 'CPTC_Follow_Up_Bill.pdf' with billAmount 3500."
