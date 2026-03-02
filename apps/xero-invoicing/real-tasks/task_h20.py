import requests


# Existing credit note IDs in seed data
SEED_CREDIT_NOTE_IDS = {"cn_001", "cn_002", "cn_003", "cn_004", "cn_005"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Greenfield Organics is con_003
    target_contact_id = "con_003"

    credit_notes = state.get("creditNotes", [])
    new_cn = None
    for cn in credit_notes:
        if cn.get("contactId") == target_contact_id and cn.get("id") not in SEED_CREDIT_NOTE_IDS:
            new_cn = cn
            break

    if new_cn is None:
        return False, "No new credit note found for Greenfield Organics (con_003)."

    # Check status is awaiting_payment (approved)
    status = new_cn.get("status", "")
    if status != "awaiting_payment":
        return False, f"Credit note status is '{status}', expected 'awaiting_payment' (approved)."

    # Check at least one line item with quantity == 5 and unitPrice approximately 24.95 (WIDGET-A)
    line_items = new_cn.get("lineItems", [])
    if not line_items:
        return False, "New credit note has no line items."

    found_widget = False
    for li in line_items:
        quantity = li.get("quantity", 0)
        unit_price = li.get("unitPrice", 0)
        if quantity == 5 and abs(unit_price - 24.95) < 1.00:
            found_widget = True
            break

    if not found_widget:
        items_info = [(li.get("quantity"), li.get("unitPrice")) for li in line_items]
        return False, f"No line item with quantity=5 and unitPrice approximately $24.95 (Widget A) found. Line items (qty, price): {items_info}."

    return True, f"Credit note '{new_cn.get('number')}' issued to Greenfield Organics for 5x Widget A at $24.95 and approved (awaiting_payment)."
