import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0052"), None)
    if not inv:
        return False, "Invoice INV-0052 not found."

    if not inv.get("payments"):
        return False, "No payments recorded on INV-0052."

    total_paid = sum(p["amount"] for p in inv["payments"])
    if abs(total_paid - 5000.00) > 0.01 and not any(abs(p["amount"] - 5000.00) < 0.01 for p in inv["payments"]):
        return False, f"No $5,000 payment found. Total paid: {total_paid}."

    if inv["status"] == "paid":
        return False, "Invoice should not be fully paid (it was a partial payment)."

    return True, f"$5,000 partial payment recorded on INV-0052."
