import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    show_discount_column = invoice_settings.get("showDiscountColumn")

    if show_discount_column is not False:
        return False, f"Discount column is not turned off. showDiscountColumn is {show_discount_column}."

    return True, "Discount column has been successfully turned off."
