import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The only draft quote is QU-0025 (Fresh Start Catering, con_022).
    quo = None
    for q in state.get("quotes", []):
        if q.get("number") == "QU-0025":
            quo = q
            break

    if quo is None:
        return False, "Quote QU-0025 not found."

    tax_mode = quo.get("taxMode", "")
    if tax_mode != "exclusive":
        return False, (
            f"QU-0025 taxMode is '{tax_mode}', expected 'exclusive'."
        )

    status = quo.get("status", "")
    if status != "sent":
        return False, (
            f"QU-0025 status is '{status}', expected 'sent'."
        )

    return True, (
        "QU-0025 (only draft quote, Fresh Start Catering) edited: "
        "tax mode changed to exclusive, then sent."
    )
