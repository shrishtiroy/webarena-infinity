import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    reminders = state.get("invoiceReminders", state.get("reminders", []))
    if not reminders:
        return False, "No invoice reminders found in state."

    target = None
    for reminder in reminders:
        if reminder.get("timing") == "after" and reminder.get("days") == 1:
            target = reminder
            break

    if target is None:
        return False, "Could not find a reminder with timing 'after' and days == 1."

    expected_subject = "Payment Required - {InvoiceNumber}"
    actual_subject = target.get("subject", "")
    if actual_subject != expected_subject:
        return False, f"Expected subject '{expected_subject}', but found '{actual_subject}'."

    return True, "1-day overdue reminder subject updated to 'Payment Required - {InvoiceNumber}'."
