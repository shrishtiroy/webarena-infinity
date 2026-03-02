import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    target = None
    for inv in invoices:
        if inv.get("number") == "INV-0056":
            target = inv
            break

    if target is None:
        return False, "Could not find invoice with number 'INV-0056'."

    status = target.get("status", "")
    if status != "awaiting_payment":
        return False, f"Invoice INV-0056 status is '{status}', expected 'awaiting_payment' (approved)."

    sent_at = target.get("sentAt")
    if sent_at is None:
        return False, "Invoice INV-0056 has been approved but sentAt is None — it has not been sent."

    return True, "Invoice INV-0056 (Horizon Media) has been approved (awaiting_payment) and sent."
