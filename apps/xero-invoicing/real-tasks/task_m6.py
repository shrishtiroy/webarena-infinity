import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    ri = next((r for r in state["repeatingInvoices"] if r["id"] == "rep_002"), None)
    if not ri:
        return False, "Repeating invoice rep_002 not found."

    if ri["frequency"] != "quarterly":
        return False, f"Frequency is '{ri['frequency']}', expected 'quarterly'."

    return True, "CloudNine Analytics repeating invoice changed to quarterly."
