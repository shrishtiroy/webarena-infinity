import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    for invoice in invoices:
        if invoice.get("number") == "INV-0057":
            status = invoice.get("status")
            sent_at = invoice.get("sentAt")

            if status != "awaiting_payment":
                return False, f"Invoice INV-0057 has status '{status}', expected 'awaiting_payment'."
            if sent_at is None:
                return False, "Invoice INV-0057 has sentAt as null, expected a non-null value."

            return True, "Invoice INV-0057 (Stellar Education Services) has been successfully marked as sent."

    return False, "Invoice INV-0057 (Stellar Education Services) not found."
