import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Create contact Kaitiaki Environmental Services, create draft invoice
    with 2 line items, then approve."""
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

    # Find the contact
    contact = next(
        (c for c in contacts if c.get("name") == "Kaitiaki Environmental Services"),
        None,
    )
    if contact is None:
        return False, "Contact 'Kaitiaki Environmental Services' not found"

    contact_id = contact.get("id")

    # Verify contact fields
    if contact.get("email") != "info@kaitiaki.co.nz":
        errors.append(f"Contact email is '{contact.get('email')}', expected 'info@kaitiaki.co.nz'")
    if contact.get("phone") != "+64 6 835 2200":
        errors.append(f"Contact phone is '{contact.get('phone')}', expected '+64 6 835 2200'")

    addr = contact.get("billingAddress", {}) or {}
    expected_addr = {
        "street": "15 Tennyson Street",
        "city": "Napier",
        "region": "Hawke's Bay",
        "postalCode": "4110",
        "country": "New Zealand",
    }
    for field, expected_val in expected_addr.items():
        actual = (addr.get(field) or "").strip()
        if actual != expected_val:
            errors.append(f"billingAddress.{field} is '{actual}', expected '{expected_val}'")

    # Find an approved invoice for this contact
    approved_inv = next(
        (inv for inv in invoices
         if inv.get("contactId") == contact_id
         and inv.get("status") == "awaiting_payment"),
        None,
    )
    if approved_inv is None:
        errors.append("No approved invoice found for Kaitiaki Environmental Services")
        return False, "; ".join(errors)

    # Check line items
    line_items = approved_inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line items, expected 2")

    eia = next((li for li in line_items if "impact assessment" in (li.get("description") or "").lower()), None)
    if eia is None:
        errors.append("No line item with description containing 'impact assessment'")
    else:
        if eia.get("quantity") != 1:
            errors.append(f"Impact assessment qty is {eia.get('quantity')}, expected 1")
        if abs((eia.get("unitPrice") or 0) - 5500) > 0.01:
            errors.append(f"Impact assessment unitPrice is {eia.get('unitPrice')}, expected 5500")

    srp = next((li for li in line_items if "remediation" in (li.get("description") or "").lower()), None)
    if srp is None:
        errors.append("No line item with description containing 'remediation'")
    else:
        if srp.get("quantity") != 1:
            errors.append(f"Remediation qty is {srp.get('quantity')}, expected 1")
        if abs((srp.get("unitPrice") or 0) - 3200) > 0.01:
            errors.append(f"Remediation unitPrice is {srp.get('unitPrice')}, expected 3200")

    # Check dates and reference
    if approved_inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{approved_inv.get('issueDate')}', expected '2026-03-18'")
    if approved_inv.get("dueDate") != "2026-05-17":
        errors.append(f"dueDate is '{approved_inv.get('dueDate')}', expected '2026-05-17'")
    if approved_inv.get("reference") != "KAIT-2026-001":
        errors.append(f"reference is '{approved_inv.get('reference')}', expected 'KAIT-2026-001'")

    if errors:
        return False, "; ".join(errors)
    return True, "Contact created and invoice approved with correct details"
