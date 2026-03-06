import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    rem = next((r for r in state["invoiceReminders"] if r["timing"] == "after" and r["days"] == 1), None)
    if not rem:
        return False, "1-day overdue reminder not found."

    expected = "Payment Required - {InvoiceNumber}"
    if rem["subject"] != expected:
        return False, f"Subject is '{rem['subject']}', expected '{expected}'."

    return True, "1-day overdue reminder subject updated."
