import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    ri = next((r for r in state["repeatingInvoices"] if r["id"] == "rep_003"), None)
    if not ri:
        return False, "Repeating invoice rep_003 not found."

    if ri["reference"] != "Cascade monthly license":
        return False, f"Reference is '{ri['reference']}', expected 'Cascade monthly license'."

    return True, "Cascade Software repeating invoice reference updated."
