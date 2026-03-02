import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    for invoice in invoices:
        if invoice.get("number") == "INV-0060":
            status = invoice.get("status")
            if status == "awaiting_approval":
                return True, "Invoice INV-0060 (Redback Mining Supplies) has been successfully submitted for approval."
            else:
                return False, f"Invoice INV-0060 has status '{status}', expected 'awaiting_approval'."

    return False, "Invoice INV-0060 (Redback Mining Supplies) not found."
