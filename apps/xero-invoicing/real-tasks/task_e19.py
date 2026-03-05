import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoice_reminders = state.get("invoiceReminders", [])
    for reminder in invoice_reminders:
        if reminder.get("timing") == "after" and reminder.get("days") == 14:
            return False, "Two-week overdue reminder (timing='after', days=14) still exists."

    return True, "Two-week overdue reminder has been successfully deleted."
