import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    reminder = next(
        (r for r in state["invoiceReminders"] if r["timing"] == "before" and r["days"] == 7),
        None
    )
    if not reminder:
        return False, "No invoice reminder found with timing 'before' and days 7."

    if reminder["enabled"] is not False:
        return False, f"Upcoming-due-date reminder enabled is {reminder['enabled']}, expected False."

    return True, "Upcoming-due-date invoice reminder (7 days before) is now disabled."
