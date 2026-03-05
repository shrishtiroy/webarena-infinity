import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing credit note numbers in seed data
    seed_cn_numbers = {"CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"}

    # Greenfield Organics = con_003
    target_contact_id = "con_003"

    credit_notes = state.get("creditNotes", [])
    new_cn = None
    for cn in credit_notes:
        if cn.get("number") in seed_cn_numbers:
            continue
        if cn.get("contactId") == target_contact_id:
            new_cn = cn
            break

    if new_cn is None:
        return False, "No new credit note found for Greenfield Organics (con_003)."

    line_items = new_cn.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"New credit note '{new_cn.get('number')}' has no line items."

    # Check that at least one line item has unitPrice ~100.00
    found_price = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        if abs(price - 100.00) < 5.00:
            found_price = True
            break

    if not found_price:
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with unitPrice ~100.00. "
            f"Found prices: {prices}."
        )

    # Check total >= 100 (task says "$100" which could mean before or after GST)
    total = float(new_cn.get("total", 0))
    if total < 100.00 - 0.01:
        return False, f"Credit note total is ${total:.2f}, expected at least $100.00."

    return True, (
        f"New credit note '{new_cn.get('number')}' created for Greenfield Organics "
        f"with a $100.00 hosting credit (total: ${total:.2f})."
    )
