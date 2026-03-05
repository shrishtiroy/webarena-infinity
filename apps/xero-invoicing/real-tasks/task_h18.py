import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    quotes = state.get("quotes", [])
    target = None
    for q in quotes:
        if q.get("number") == "QU-0025":
            target = q
            break

    if target is None:
        return False, "Could not find quote with number 'QU-0025'."

    # Check expiryDate is 2026-04-30
    expiry_date = target.get("expiryDate", "")
    if expiry_date != "2026-04-30":
        return False, f"Quote QU-0025 expiryDate is '{expiry_date}', expected '2026-04-30'."

    # Check status is sent
    status = target.get("status", "")
    if status != "sent":
        return False, f"Quote QU-0025 status is '{status}', expected 'sent'."

    # Check sentAt is not None
    sent_at = target.get("sentAt")
    if sent_at is None:
        return False, "Quote QU-0025 has status 'sent' but sentAt is None."

    return True, "Quote QU-0025 (Fresh Start Catering) expiry extended to 2026-04-30 and sent."
