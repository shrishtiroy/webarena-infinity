import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find credit note CN-0012 (CloudNine Analytics, con_007)
    credit_notes = state.get("creditNotes", [])
    cn = None
    for c in credit_notes:
        if c.get("number") == "CN-0012":
            cn = c
            break

    if cn is None:
        return False, "Credit note CN-0012 not found."

    # Check it has at least one allocation
    allocations = cn.get("allocations", [])
    if len(allocations) < 1:
        return False, "Credit note CN-0012 has no allocations."

    # Find the allocation targeting INV-0047 (CloudNine's largest outstanding invoice)
    target_allocation = None
    for alloc in allocations:
        if alloc.get("invoiceNumber") == "INV-0047":
            target_allocation = alloc
            break

    if target_allocation is None:
        alloc_invoices = [a.get("invoiceNumber") for a in allocations]
        return False, (
            f"No allocation found for INV-0047. "
            f"Allocations target invoices: {alloc_invoices}."
        )

    # Check allocation amount is approximately 2035.00
    alloc_amount = float(target_allocation.get("amount", 0))
    if abs(alloc_amount - 2035.00) > 5.00:
        return False, (
            f"Allocation amount is ${alloc_amount:.2f}, expected ~$2035.00."
        )

    # Check remainingCredit is approximately 0
    remaining = float(cn.get("remainingCredit", 9999))
    if remaining > 1.00:
        return False, (
            f"CN-0012 remainingCredit is ${remaining:.2f}, expected ~$0."
        )

    # Check CN-0012 status is "paid"
    status = cn.get("status", "")
    if status != "paid":
        return False, (
            f"CN-0012 status is '{status}', expected 'paid'."
        )

    return True, (
        "Credit note CN-0012 ($2,035) applied against INV-0047 ($18,652.70), "
        "the largest outstanding CloudNine Analytics invoice."
    )
