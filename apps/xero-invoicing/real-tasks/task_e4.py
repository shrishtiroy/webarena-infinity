import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    quote = next((q for q in state["quotes"] if q["number"] == "QU-0023"), None)
    if not quote:
        return False, "Quote QU-0023 not found."

    if quote["status"] != "accepted":
        return False, f"Quote QU-0023 status is '{quote['status']}', expected 'accepted'."

    return True, "Quote QU-0023 (Redback Mining) accepted successfully."
