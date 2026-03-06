import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    rem = next((r for r in state["invoiceReminders"]
                if r["timing"] == "after" and r["days"] == 21), None)

    if not rem:
        return False, "21-day overdue reminder not found."

    if not rem.get("enabled", False):
        return False, "21-day overdue reminder is not enabled."

    return True, "21-day overdue reminder added and enabled."
