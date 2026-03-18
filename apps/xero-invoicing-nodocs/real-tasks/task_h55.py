import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Copy INV-0022 for Meridian Health Clinic, change contact to Redwood
    Property Management, update reference to RPM-TRANSFER-001, save as draft."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    errors = []

    # Find Redwood Property Management
    redwood = next(
        (c for c in contacts if c.get("name") == "Redwood Property Management"),
        None,
    )
    if redwood is None:
        return False, "Contact 'Redwood Property Management' not found"

    redwood_id = redwood.get("id")

    # Find a draft invoice for Redwood with reference RPM-TRANSFER-001
    copy_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == redwood_id
         and inv.get("status") == "draft"
         and inv.get("reference") == "RPM-TRANSFER-001"),
        None,
    )
    if copy_inv is None:
        # Try any draft for Redwood
        any_draft = next(
            (inv for inv in invoices
             if inv.get("contactId") == redwood_id and inv.get("status") == "draft"),
            None,
        )
        if any_draft is None:
            return False, "No draft invoice found for Redwood Property Management"
        errors.append(
            f"Draft found but reference is '{any_draft.get('reference')}', "
            f"expected 'RPM-TRANSFER-001'"
        )
        copy_inv = any_draft

    # Check line items match INV-0022 (1 line item: Environmental impact assessment, qty 100, $2500)
    line_items = copy_inv.get("lineItems", [])
    if len(line_items) != 1:
        errors.append(f"Copy has {len(line_items)} line items, expected 1 (matching INV-0022)")

    if line_items:
        li = line_items[0]
        desc = (li.get("description") or "").lower()
        if "environmental" not in desc or "impact" not in desc or "assessment" not in desc:
            errors.append(f"Line item description is '{li.get('description')}', expected to contain 'Environmental impact assessment'")
        if li.get("quantity") != 100:
            errors.append(f"Line item qty is {li.get('quantity')}, expected 100")
        if abs((li.get("unitPrice") or 0) - 2500) > 0.01:
            errors.append(f"Line item unitPrice is {li.get('unitPrice')}, expected 2500")

    if errors:
        return False, "; ".join(errors)
    return True, f"INV-0022 copied to Redwood Property Management as draft with reference RPM-TRANSFER-001"
