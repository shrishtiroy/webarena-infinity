import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_settings = state.get("invoiceSettings", {})
    default_due_date = invoice_settings.get("defaultDueDate", {})
    due_type = default_due_date.get("type", "")

    if due_type != "endOfFollowingMonth":
        return False, f"Expected defaultDueDate type 'endOfFollowingMonth', but found '{due_type}'."

    return True, "Default payment terms set to end of following month."
