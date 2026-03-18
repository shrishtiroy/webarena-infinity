import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Edit draft INV-0054: change reference, branding, add line item, approve."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    inv = next((i for i in invoices if i.get("invoiceNumber") == "INV-0054"), None)
    if inv is None:
        return False, "INV-0054 not found"

    # Check status is approved
    if inv.get("status") != "awaiting_payment":
        errors.append(f"status is '{inv.get('status')}', expected 'awaiting_payment'")

    # Check reference
    if inv.get("reference") != "NEXUS-REVISED-2026":
        errors.append(f"reference is '{inv.get('reference')}', expected 'NEXUS-REVISED-2026'")

    # Check branding theme
    if inv.get("brandingThemeId") != "theme_3":
        errors.append(f"brandingThemeId is '{inv.get('brandingThemeId')}', expected 'theme_3' (Minimal Clean)")

    # Check line items: original 2 + 1 new = 3
    line_items = inv.get("lineItems", [])
    if len(line_items) != 3:
        errors.append(f"Invoice has {len(line_items)} line items, expected 3")

    # Check for the new line item
    pmo = next(
        (li for li in line_items
         if "project management" in (li.get("description") or "").lower()),
        None,
    )
    if pmo is None:
        errors.append("No line item with description containing 'project management'")
    else:
        if pmo.get("quantity") != 1:
            errors.append(f"Project management qty is {pmo.get('quantity')}, expected 1")
        if abs((pmo.get("unitPrice") or 0) - 500) > 0.01:
            errors.append(f"Project management unitPrice is {pmo.get('unitPrice')}, expected 500")

    if errors:
        return False, "; ".join(errors)
    return True, "INV-0054 updated with new reference, branding theme, line item, and approved"
