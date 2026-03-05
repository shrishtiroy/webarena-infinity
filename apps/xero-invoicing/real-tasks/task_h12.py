import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})

    prefix = invoice_settings.get("invoicePrefix", "")
    if prefix != "TAX-":
        return False, f"Expected invoicePrefix 'TAX-', but found '{prefix}'."

    next_number = invoice_settings.get("invoiceNextNumber")
    if next_number != 100:
        return False, f"Expected invoiceNextNumber 100, but found {next_number}."

    return True, "Invoice numbering updated: prefix is 'TAX-' and next number is 100."
