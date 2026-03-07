import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Northwestern Memorial Hospital"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Northwestern Memorial Hospital"), None)
    if not contact:
        return False, "Contact 'Northwestern Memorial Hospital' not found."

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
        return False, "No medical provider with contactId for 'Northwestern Memorial Hospital' found on matter 'Rodriguez v. Premier Auto'."

    # Find medical bill with fileName "NM_Hospital_Bill.pdf"
    bill = next(
        (b for b in provider.get("medicalBills", []) if b.get("fileName") == "NM_Hospital_Bill.pdf"),
        None
    )
    if not bill:
        existing = [b.get("fileName") for b in provider.get("medicalBills", [])]
        return False, f"No medical bill with fileName 'NM_Hospital_Bill.pdf' found. Existing bills: {existing}"

    adjustment = bill.get("adjustment")
    if adjustment != 7000:
        return False, f"Medical bill 'NM_Hospital_Bill.pdf' has adjustment {adjustment}, expected 7000."

    return True, "Provider 'Northwestern Memorial Hospital' on matter 'Rodriguez v. Premier Auto' has medical bill 'NM_Hospital_Bill.pdf' with adjustment 7000."
