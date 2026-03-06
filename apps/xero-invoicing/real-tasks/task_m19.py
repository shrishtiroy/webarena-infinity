import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0045"), None)
    if not inv:
        return False, "Invoice INV-0045 not found."

    if inv["payments"]:
        return False, f"Invoice INV-0045 still has {len(inv['payments'])} payment(s)."

    if inv["amountPaid"] != 0:
        return False, f"Invoice INV-0045 amountPaid is {inv['amountPaid']}, expected 0."

    if abs(inv["amountDue"] - inv["total"]) > 0.01:
        return False, f"Invoice INV-0045 amountDue ({inv['amountDue']}) does not match total ({inv['total']})."

    return True, "Partial payment on INV-0045 reversed."
