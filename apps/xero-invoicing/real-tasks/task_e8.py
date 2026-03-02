import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    reminder = next(
        (r for r in state["invoiceReminders"] if r["timing"] == "after" and r["days"] == 30),
        None
    )
    if not reminder:
        return False, "No invoice reminder found with timing 'after' and days 30."

    if reminder["enabled"] is not True:
        return False, f"30-day overdue reminder enabled is {reminder['enabled']}, expected True."

    return True, "30-day overdue invoice reminder is now enabled."
