import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    repeating_invoices = state.get("repeatingInvoices", [])
    for invoice in repeating_invoices:
        if invoice.get("id") == "rep_005":
            return False, "Repeating invoice 'rep_005' (Summit Health Group) still exists."

    return True, "Summit Health Group repeating invoice (rep_005) has been successfully cancelled."
