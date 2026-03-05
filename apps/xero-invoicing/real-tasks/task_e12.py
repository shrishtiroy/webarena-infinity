import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    show_tax_column = invoice_settings.get("showTaxColumn")

    if show_tax_column is not False:
        return False, f"Tax column is not hidden. showTaxColumn is {show_tax_column}."

    return True, "Tax column has been successfully hidden on invoices."
