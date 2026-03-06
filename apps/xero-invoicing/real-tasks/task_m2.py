import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0045"), None)
    if not inv:
        return False, "Invoice INV-0045 not found."

    if inv["status"] != "paid":
        return False, f"Invoice INV-0045 status is '{inv['status']}', expected 'paid'."

    if inv["amountDue"] != 0:
        return False, f"Invoice INV-0045 amountDue is {inv['amountDue']}, expected 0."

    if abs(inv["amountPaid"] - inv["total"]) > 0.01:
        return False, f"Invoice INV-0045 amountPaid ({inv['amountPaid']}) does not match total ({inv['total']})."

    return True, "Invoice INV-0045 fully paid (remaining balance closed)."
