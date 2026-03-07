import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Advanced Imaging Associates"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Advanced Imaging Associates"), None)
    if not contact:
        return False, "Contact 'Advanced Imaging Associates' not found."

    # Find matter "Rodriguez v. Premier Auto"
    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find provider - it might have been deleted entirely, which is also a pass
    provider = next(
        (p for p in matter.get("medicalProviders", []) if p["contactId"] == contact["id"]),
        None
    )
    if not provider:
        return True, "Provider 'Advanced Imaging Associates' was removed from matter 'Rodriguez v. Premier Auto' entirely. Bill 'AIA_Invoice_Aug.pdf' does not exist."

    # Provider exists - check that the specific bill is gone
    bill = next(
        (b for b in provider.get("medicalBills", []) if b.get("fileName") == "AIA_Invoice_Aug.pdf"),
        None
    )
    if bill is not None:
        return False, (
            f"Medical bill 'AIA_Invoice_Aug.pdf' still exists on provider 'Advanced Imaging Associates' "
            f"(bill id: {bill.get('id')})."
        )

    return True, "Provider 'Advanced Imaging Associates' on matter 'Rodriguez v. Premier Auto' does not have medical bill 'AIA_Invoice_Aug.pdf'."
