import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Smallest awaiting-payment invoice: INV-0053 ($823.90, Vanguard Security).
    # Draft invoices: INV-0058, INV-0059, INV-0060.
    inv_0053 = None
    for i in state.get("invoices", []):
        if i.get("number") == "INV-0053":
            inv_0053 = i
            break

    if inv_0053 is None:
        return False, "Invoice INV-0053 not found."

    if inv_0053.get("status") != "voided":
        return False, (
            f"INV-0053 status is '{inv_0053.get('status')}', expected 'voided'."
        )

    # Check all draft invoices are deleted
    draft_numbers = ["INV-0058", "INV-0059", "INV-0060"]
    for num in draft_numbers:
        inv = None
        for i in state.get("invoices", []):
            if i.get("number") == num:
                inv = i
                break
        if inv is None:
            continue  # Deleted entirely is also acceptable
        if inv.get("status") != "deleted":
            return False, (
                f"{num} status is '{inv.get('status')}', expected 'deleted'."
            )

    return True, (
        "INV-0053 (smallest awaiting-payment, $823.90) voided. "
        "All draft invoices (INV-0058, INV-0059, INV-0060) deleted."
    )
