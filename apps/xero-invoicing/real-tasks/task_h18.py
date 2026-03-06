import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    quo = next((q for q in state["quotes"] if q["number"] == "QU-0025"), None)
    if not quo:
        return False, "Quote QU-0025 not found."

    if quo["expiryDate"] != "2026-04-30":
        return False, f"Expiry date is '{quo['expiryDate']}', expected '2026-04-30'."

    if quo["status"] != "sent":
        return False, f"Quote status is '{quo['status']}', expected 'sent'."

    if not quo.get("sentAt"):
        return False, "Quote sentAt is null."

    return True, "Quote QU-0025 expiry extended to April 30 and sent."
