import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    reminders = state.get("invoiceReminders", [])
    if not reminders:
        return False, "No invoice reminders found in state."

    # Look for a reminder with timing == "after" and days == 21
    target = None
    for r in reminders:
        if r.get("timing") == "after" and r.get("days") == 21:
            target = r
            break

    if target is None:
        existing = [(r.get("timing"), r.get("days")) for r in reminders]
        return False, (
            f"No reminder found with timing 'after' and days 21. "
            f"Existing reminders (timing, days): {existing}."
        )

    if not target.get("enabled"):
        return False, "21-day overdue reminder found but it is not enabled."

    expected_subject = "Third reminder: Invoice overdue - {InvoiceNumber}"
    actual_subject = target.get("subject", "")
    if actual_subject != expected_subject:
        return False, (
            f"21-day reminder subject is '{actual_subject}', "
            f"expected '{expected_subject}'."
        )

    expected_body = (
        "Dear {ContactName}, Invoice {InvoiceNumber} is now 21 days past due. "
        "Please arrange immediate payment."
    )
    actual_body = target.get("body", "")
    if actual_body != expected_body:
        return False, (
            f"21-day reminder body does not match expected text. "
            f"Got: '{actual_body}'."
        )

    return True, "21-day overdue reminder added with correct subject and body."
