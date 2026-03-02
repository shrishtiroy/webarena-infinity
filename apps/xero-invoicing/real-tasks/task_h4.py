import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing credit note numbers in seed data
    seed_cn_numbers = {"CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"}

    # TechVault Solutions Pty Ltd = con_002
    target_contact_id = "con_002"

    credit_notes = state.get("creditNotes", [])
    new_cn = None
    for cn in credit_notes:
        if cn.get("number") in seed_cn_numbers:
            continue
        if cn.get("contactId") == target_contact_id:
            new_cn = cn
            break

    if new_cn is None:
        return False, "No new credit note found for TechVault Solutions Pty Ltd (con_002)."

    # Check status is "awaiting_payment" (approved)
    status = new_cn.get("status", "")
    if status != "awaiting_payment":
        return False, (
            f"New credit note '{new_cn.get('number')}' status is '{status}', "
            f"expected 'awaiting_payment' (approved)."
        )

    line_items = new_cn.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"New credit note '{new_cn.get('number')}' has no line items."

    # Check for a line item with quantity 4 and unitPrice ~25.00
    found_match = False
    for li in line_items:
        qty = li.get("quantity", 0)
        price = li.get("unitPrice", 0)
        if qty == 4 and abs(float(price) - 25.00) < 1.00:
            found_match = True
            break

    if not found_match:
        quantities = [li.get("quantity") for li in line_items]
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with quantity 4 and unitPrice ~25.00. "
            f"Found quantities: {quantities}, prices: {prices}."
        )

    return True, (
        f"New credit note '{new_cn.get('number')}' created and approved for TechVault Solutions "
        f"covering a $25/hour rate adjustment for 4 hours."
    )
