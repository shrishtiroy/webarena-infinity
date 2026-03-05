import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    reminders = state.get("invoiceReminders", [])

    # rem_003: 14-day after, should be disabled
    rem_14 = None
    for r in reminders:
        if r.get("id") == "rem_003":
            rem_14 = r
            break

    if rem_14 is None:
        return False, "Reminder rem_003 (14-day overdue) not found."

    if rem_14.get("enabled") is not False:
        return False, (
            f"14-day overdue reminder enabled is {rem_14.get('enabled')}, expected False."
        )

    # rem_004: 30-day after, should be enabled with new subject
    rem_30 = None
    for r in reminders:
        if r.get("id") == "rem_004":
            rem_30 = r
            break

    if rem_30 is None:
        return False, "Reminder rem_004 (30-day overdue) not found."

    if rem_30.get("enabled") is not True:
        return False, (
            f"30-day overdue reminder enabled is {rem_30.get('enabled')}, expected True."
        )

    expected_subject = "Urgent: Invoice {InvoiceNumber} requires immediate payment"
    actual_subject = rem_30.get("subject", "")
    if actual_subject != expected_subject:
        return False, (
            f"30-day reminder subject is '{actual_subject}', "
            f"expected '{expected_subject}'."
        )

    return True, (
        "14-day overdue reminder disabled. 30-day overdue reminder enabled "
        "with subject 'Urgent: Invoice {InvoiceNumber} requires immediate payment'."
    )
