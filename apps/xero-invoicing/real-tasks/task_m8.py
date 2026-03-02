import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    prefix = invoice_settings.get("invoicePrefix")

    if prefix != "TAX-":
        return False, f"Invoice prefix is '{prefix}', expected 'TAX-'."

    return True, "Invoice number prefix has been updated to 'TAX-'."
