import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing repeating invoice IDs in seed data
    seed_rep_ids = {"rep_001", "rep_002", "rep_003", "rep_004", "rep_005"}

    # Bright Spark Electrical = con_013
    target_contact_id = "con_013"

    repeating = state.get("repeatingInvoices", [])
    new_rep = None
    for r in repeating:
        if r.get("id") in seed_rep_ids:
            continue
        if r.get("contactId") == target_contact_id:
            new_rep = r
            break

    if new_rep is None:
        return False, "No new repeating invoice found for Bright Spark Electrical (con_013)."

    frequency = new_rep.get("frequency", "")
    if frequency != "monthly":
        return False, f"Repeating invoice frequency is '{frequency}', expected 'monthly'."

    start_date = new_rep.get("startDate", "")
    if start_date != "2026-04-01":
        return False, f"Repeating invoice startDate is '{start_date}', expected '2026-04-01'."

    line_items = new_rep.get("lineItems", [])
    if len(line_items) < 1:
        return False, "New repeating invoice has no line items."

    # Check for a line item with unitPrice ~299.00
    found_price = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        if abs(price - 299.00) < 1.00:
            found_price = True
            break

    if not found_price:
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with unitPrice ~299.00. "
            f"Found prices: {prices}."
        )

    return True, (
        f"New monthly repeating invoice created for Bright Spark Electrical "
        f"for cloud hosting at ~$299/month starting 2026-04-01."
    )
