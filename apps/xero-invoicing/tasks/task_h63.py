import requests


SEED_QUOTE_IDS = {
    "quo_001", "quo_002", "quo_003", "quo_004",
    "quo_005", "quo_006", "quo_007", "quo_008",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Contacts with paid invoices and their totals:
    # con_001: $15,840 | con_002: $8,756 | con_003: $749 | con_011: $2,370.25
    # con_016: $3,000 | con_017: $23,100
    # Smallest paid total: Greenfield Organics (con_003) at $749.
    new_quo = None
    for q in state.get("quotes", []):
        if q.get("contactId") == "con_003" and q.get("id") not in SEED_QUOTE_IDS:
            new_quo = q
            break

    if new_quo is None:
        return False, "No new quote found for Greenfield Organics (con_003)."

    status = new_quo.get("status", "")
    if status != "draft":
        return False, (
            f"New quote status is '{status}', expected 'draft'."
        )

    # Check line item: 2 days project management at ~$1,400
    line_items = new_quo.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 1400.00) < 50.00 and qty == 2:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 2 and unitPrice ~$1,400 (project management) found. "
            f"Items: {items}."
        )

    return True, (
        f"Greenfield Organics (smallest paid total at $749) identified. "
        f"Draft quote '{new_quo.get('number')}' created for 2 days of project management."
    )
