import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    cn = next((c for c in state["creditNotes"] if c["number"] == "CN-0012"), None)
    if not cn:
        return False, "Credit note CN-0012 not found."

    inv = next((i for i in state["invoices"] if i["number"] == "INV-0047"), None)
    if not inv:
        return False, "Invoice INV-0047 not found."

    if not cn.get("allocations"):
        return False, "CN-0012 has no allocations."

    alloc = next((a for a in cn["allocations"] if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "CN-0012 not allocated to INV-0047."

    if abs(alloc["amount"] - 2035.00) > 0.01:
        return False, f"Allocation amount is {alloc['amount']}, expected 2035.00."

    if cn["remainingCredit"] > 0.01:
        return False, f"CN-0012 remainingCredit is {cn['remainingCredit']}, expected 0."

    return True, "CN-0012 allocated to INV-0047 (CloudNine's largest invoice)."
