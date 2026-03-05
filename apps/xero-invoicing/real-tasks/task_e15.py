import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    show_item_code = invoice_settings.get("showItemCode")

    if show_item_code is not False:
        return False, f"Item codes are still displayed. showItemCode is {show_item_code}."

    return True, "Item codes have been successfully hidden on invoices."
