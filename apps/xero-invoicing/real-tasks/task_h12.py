import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("invoiceSettings", {})

    if settings.get("invoicePrefix") != "TAX-":
        return False, f"Invoice prefix is '{settings.get('invoicePrefix')}', expected 'TAX-'."

    next_num = settings.get("invoiceNextNumber", state.get("_nextInvoiceNum"))
    if next_num != 100:
        return False, f"Next invoice number is {next_num}, expected 100."

    return True, "Invoice numbering changed to TAX-0100."
