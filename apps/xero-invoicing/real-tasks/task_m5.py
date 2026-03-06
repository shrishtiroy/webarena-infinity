import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    cn = next((c for c in state["creditNotes"] if c["number"] == "CN-0009"), None)
    if not cn:
        return False, "Credit note CN-0009 not found."

    inv = next((i for i in state["invoices"] if i["number"] == "INV-0049"), None)
    if not inv:
        return False, "Invoice INV-0049 not found."

    if not cn.get("allocations"):
        return False, "Credit note CN-0009 has no allocations."

    alloc = next((a for a in cn["allocations"] if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "Credit note CN-0009 not allocated to INV-0049."

    if abs(alloc["amount"] - 249.75) > 0.01:
        return False, f"Allocation amount is {alloc['amount']}, expected 249.75."

    if cn["remainingCredit"] > 0.01:
        return False, f"Credit note remaining credit is {cn['remainingCredit']}, expected 0."

    return True, "Credit note CN-0009 allocated to INV-0049."
