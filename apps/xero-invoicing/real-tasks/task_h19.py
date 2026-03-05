import requests


# Atlas Engineering Consultants (con_025) has no existing invoices in seed data
SEED_INVOICE_IDS = set()


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Atlas Engineering Consultants is con_025
    target_contact_id = "con_025"

    invoices = state.get("invoices", [])
    new_invoice = None
    for inv in invoices:
        if inv.get("contactId") == target_contact_id and inv.get("id") not in SEED_INVOICE_IDS:
            new_invoice = inv
            break

    if new_invoice is None:
        return False, "No new invoice found for Atlas Engineering Consultants (con_025)."

    # Check brandingThemeId is theme_professional
    branding_theme_id = new_invoice.get("brandingThemeId", "")
    if branding_theme_id != "theme_professional":
        return False, f"New invoice brandingThemeId is '{branding_theme_id}', expected 'theme_professional'."

    # Check at least one line item with quantity == 5 and unitPrice approximately 1400.00 (PM-DAY)
    line_items = new_invoice.get("lineItems", [])
    if not line_items:
        return False, "New invoice for Atlas Engineering has no line items."

    found_pm = False
    for li in line_items:
        quantity = li.get("quantity", 0)
        unit_price = li.get("unitPrice", 0)
        if quantity == 5 and abs(unit_price - 1400.00) < 10.00:
            found_pm = True
            break

    if not found_pm:
        items_info = [(li.get("quantity"), li.get("unitPrice")) for li in line_items]
        return False, f"No line item with quantity=5 and unitPrice approximately $1,400.00 (project management day rate) found. Line items (qty, price): {items_info}."

    return True, f"New invoice '{new_invoice.get('number')}' created for Atlas Engineering Consultants using Professional Services template with 5 days of project management at $1,400/day."
