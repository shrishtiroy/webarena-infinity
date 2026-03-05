import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find credit note CN-0009
    credit_notes = state.get("creditNotes", [])
    cn = None
    for c in credit_notes:
        if c.get("number") == "CN-0009":
            cn = c
            break

    if cn is None:
        return False, "Credit note CN-0009 not found."

    # Check it has at least one allocation
    allocations = cn.get("allocations", [])
    if len(allocations) < 1:
        return False, "Credit note CN-0009 has no allocations."

    # Find an allocation to INV-0049
    alloc_to_inv0049 = None
    for a in allocations:
        if a.get("invoiceNumber") == "INV-0049" or a.get("invoiceId") == "INV-0049":
            alloc_to_inv0049 = a
            break

    if alloc_to_inv0049 is None:
        # Also check by invoice number in nested structures
        for a in allocations:
            inv_num = a.get("invoiceNumber", "")
            inv_id = a.get("invoiceId", "")
            if "INV-0049" in str(inv_num) or "INV-0049" in str(inv_id):
                alloc_to_inv0049 = a
                break

    if alloc_to_inv0049 is None:
        return False, f"No allocation to INV-0049 found on credit note CN-0009. Allocations: {allocations}"

    # Check allocation amount is approximately 249.75
    alloc_amount = float(alloc_to_inv0049.get("amount", 0))
    if abs(alloc_amount - 249.75) >= 0.01:
        return False, f"Allocation amount to INV-0049 is {alloc_amount}, expected approximately 249.75."

    # Check CN-0009 status is "paid" (fully allocated)
    if cn.get("status") != "paid":
        return False, f"Credit note CN-0009 status is '{cn.get('status')}', expected 'paid'."

    # Check remainingCredit is approximately 0
    remaining = float(cn.get("remainingCredit", -1))
    if abs(remaining) >= 0.01:
        return False, f"Credit note CN-0009 remainingCredit is {remaining}, expected approximately 0."

    return True, "Credit note CN-0009 has been fully allocated against invoice INV-0049 (Coastal Living Interiors)."
