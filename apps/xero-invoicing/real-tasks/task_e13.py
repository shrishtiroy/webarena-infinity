import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    default_tax_mode = invoice_settings.get("defaultTaxMode")

    if default_tax_mode != "inclusive":
        return False, f"Default tax mode is '{default_tax_mode}', expected 'inclusive'."

    return True, "Default tax mode has been successfully switched to tax-inclusive."
