import requests


# Existing repeating invoice IDs in seed data
SEED_REPEATING_IDS = {"rep_001", "rep_002", "rep_003", "rep_004", "rep_005"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Harbour City Plumbing is con_021
    target_contact_id = "con_021"

    repeating_invoices = state.get("repeatingInvoices", [])
    new_rep = None
    for r in repeating_invoices:
        if r.get("contactId") == target_contact_id and r.get("id") not in SEED_REPEATING_IDS:
            new_rep = r
            break

    if new_rep is None:
        return False, "No new repeating invoice found for Harbour City Plumbing (con_021)."

    # Check frequency is monthly
    frequency = new_rep.get("frequency", "")
    if frequency != "monthly":
        return False, f"Repeating invoice frequency is '{frequency}', expected 'monthly'."

    # Check saveAs is approved_for_sending (auto-sent)
    save_as = new_rep.get("saveAs", "")
    if save_as != "approved_for_sending":
        return False, f"Repeating invoice saveAs is '{save_as}', expected 'approved_for_sending'."

    # Check startDate is 2026-04-01
    start_date = new_rep.get("startDate", "")
    if start_date != "2026-04-01":
        return False, f"Repeating invoice startDate is '{start_date}', expected '2026-04-01'."

    # Check at least one line item with unitPrice approximately 299.00
    line_items = new_rep.get("lineItems", [])
    if not line_items:
        return False, "Repeating invoice has no line items."

    found_hosting = False
    for li in line_items:
        if abs(li.get("unitPrice", 0) - 299.00) < 1.00:
            found_hosting = True
            break

    if not found_hosting:
        prices = [li.get("unitPrice") for li in line_items]
        return False, f"No line item with unitPrice approximately $299.00 found. Line item prices: {prices}."

    return True, "Monthly repeating invoice for Harbour City Plumbing created with $299/month hosting, approved for sending, starting April 2026."
