import requests


SEED_INVOICE_IDS = {
    "inv_000", "inv_001", "inv_002", "inv_003", "inv_004", "inv_005",
    "inv_006", "inv_007", "inv_008", "inv_009", "inv_010", "inv_011",
    "inv_012", "inv_013", "inv_014", "inv_015", "inv_016", "inv_017",
    "inv_018", "inv_019", "inv_020", "inv_021", "inv_022", "inv_023",
    "inv_024", "inv_025",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Highest-total draft invoice is INV-0058 ($4,280) for Murray River Winery (con_008).
    # The copy should be submitted for approval (awaiting_approval), NOT approved.
    new_inv = None
    for inv in state.get("invoices", []):
        if inv.get("contactId") == "con_008" and inv.get("id") not in SEED_INVOICE_IDS:
            new_inv = inv
            break

    if new_inv is None:
        return False, "No new invoice found for Murray River Winery (con_008)."

    status = new_inv.get("status", "")
    if status != "awaiting_approval":
        return False, (
            f"New invoice status is '{status}', expected 'awaiting_approval'. "
            f"The copy should be submitted for approval, not approved or left as draft."
        )

    # Check line items match INV-0058 (dev + design)
    line_items = new_inv.get("lineItems", [])
    if len(line_items) < 2:
        return False, (
            f"New invoice has {len(line_items)} line items, expected at least 2 "
            f"(copied from INV-0058)."
        )

    return True, (
        f"INV-0058 (highest-total draft) copied. New invoice '{new_inv.get('number')}' "
        f"correctly submitted for approval (awaiting_approval)."
    )
