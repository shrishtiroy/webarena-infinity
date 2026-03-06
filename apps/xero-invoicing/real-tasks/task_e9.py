import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    rem = next((r for r in state["invoiceReminders"] if r["timing"] == "before" and r["days"] == 7), None)
    if not rem:
        return False, "7-day before-due reminder not found."

    if rem["enabled"]:
        return False, "7-day before-due reminder is still enabled."

    return True, "7-day before-due reminder disabled successfully."
