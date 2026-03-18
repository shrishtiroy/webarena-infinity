import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Change prefix to ENV-, next number to 1000, then create draft invoice
    for Clearwater Environmental."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    settings = state.get("settings", {})
    errors = []

    # Check settings
    if settings.get("invoiceNumberPrefix") != "ENV-":
        errors.append(f"invoiceNumberPrefix is '{settings.get('invoiceNumberPrefix')}', expected 'ENV-'")

    # Find Clearwater Environmental
    clearwater = next((c for c in contacts if c.get("name") == "Clearwater Environmental"), None)
    if clearwater is None:
        return False, "Contact 'Clearwater Environmental' not found; " + "; ".join(errors) if errors else "Contact not found"

    # Find draft invoice for Clearwater
    draft_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == clearwater.get("id") and inv.get("status") == "draft"
         and (inv.get("invoiceNumber") or "").startswith("ENV-")),
        None,
    )
    if draft_inv is None:
        # Try finding any new draft for Clearwater
        draft_inv = next(
            (inv for inv in invoices
             if inv.get("contactId") == clearwater.get("id") and inv.get("status") == "draft"
             and inv.get("invoiceNumber") != "INV-0042"),
            None,
        )
    if draft_inv is None:
        errors.append("No new draft invoice found for Clearwater Environmental with ENV- prefix")
        return False, "; ".join(errors)

    # Check line items
    line_items = draft_inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line items, expected 2")

    wqt = next((li for li in line_items if "water" in (li.get("description") or "").lower() and "testing" in (li.get("description") or "").lower()), None)
    if wqt is None:
        errors.append("No line item with description containing 'water' and 'testing'")
    else:
        if wqt.get("quantity") != 4:
            errors.append(f"Water testing qty is {wqt.get('quantity')}, expected 4")
        if abs((wqt.get("unitPrice") or 0) - 850) > 0.01:
            errors.append(f"Water testing unitPrice is {wqt.get('unitPrice')}, expected 850")

    cr = next((li for li in line_items if "compliance" in (li.get("description") or "").lower()), None)
    if cr is None:
        errors.append("No line item with description containing 'compliance'")
    else:
        if cr.get("quantity") != 1:
            errors.append(f"Compliance report qty is {cr.get('quantity')}, expected 1")
        if abs((cr.get("unitPrice") or 0) - 2200) > 0.01:
            errors.append(f"Compliance report unitPrice is {cr.get('unitPrice')}, expected 2200")

    # Check dates
    if draft_inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{draft_inv.get('issueDate')}', expected '2026-03-18'")
    if draft_inv.get("dueDate") != "2026-04-17":
        errors.append(f"dueDate is '{draft_inv.get('dueDate')}', expected '2026-04-17'")

    if errors:
        return False, "; ".join(errors)
    return True, f"Settings updated and draft invoice {draft_inv.get('invoiceNumber')} created for Clearwater Environmental"
