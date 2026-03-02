import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing repeating invoice IDs in seed data
    seed_rep_ids = {"rep_001", "rep_002", "rep_003", "rep_004", "rep_005"}

    # Southern Cross Veterinary = con_024
    target_contact_id = "con_024"

    repeating = state.get("repeatingInvoices", [])
    new_rep = None
    for r in repeating:
        if r.get("id") in seed_rep_ids:
            continue
        if r.get("contactId") == target_contact_id:
            new_rep = r
            break

    if new_rep is None:
        return False, "No new repeating invoice found for Southern Cross Veterinary (con_024)."

    frequency = new_rep.get("frequency", "")
    if frequency != "quarterly":
        return False, f"Repeating invoice frequency is '{frequency}', expected 'quarterly'."

    save_as = new_rep.get("saveAs", "")
    if save_as != "approved":
        return False, f"Repeating invoice saveAs is '{save_as}', expected 'approved'."

    start_date = new_rep.get("startDate", "")
    if start_date != "2026-04-01":
        return False, f"Repeating invoice startDate is '{start_date}', expected '2026-04-01'."

    line_items = new_rep.get("lineItems", [])
    if len(line_items) < 1:
        return False, "New repeating invoice has no line items."

    # Check for a line item with unitPrice ~450.00
    found_price = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        if abs(price - 450.00) < 1.00:
            found_price = True
            break

    if not found_price:
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with unitPrice ~450.00. "
            f"Found prices: {prices}."
        )

    return True, (
        f"New quarterly auto-approved repeating invoice created for Southern Cross Veterinary "
        f"for tech support at ~$450 starting 2026-04-01."
    )
