import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Void all overdue invoices for the contact whose overdue invoices have
    the highest combined total amount."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    contacts = state.get("contacts", [])
    errors = []

    # The contact with the highest combined overdue total in seed data is
    # Bloom & Branch Florists (INV-0015 $35,937.50 + INV-0040 $121,725 = $157,662.50)
    target_name = "Bloom & Branch Florists"
    target = next((c for c in contacts if c.get("name") == target_name), None)
    if target is None:
        return False, f"Contact '{target_name}' not found"

    target_id = target.get("id")

    # Verify no overdue invoices remain for this contact
    still_overdue = [
        inv for inv in invoices
        if inv.get("contactId") == target_id and inv.get("status") == "overdue"
    ]
    if still_overdue:
        nums = [inv.get("invoiceNumber") for inv in still_overdue]
        errors.append(f"Overdue invoices still exist for {target_name}: {nums}")

    # Verify at least some invoices for this contact are now voided
    voided = [
        inv for inv in invoices
        if inv.get("contactId") == target_id and inv.get("status") == "voided"
    ]
    if not voided:
        errors.append(f"No voided invoices found for {target_name}")

    # Verify specific invoices are voided
    for inv_num in ["INV-0015", "INV-0040"]:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
        elif inv.get("status") != "voided":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'voided'")

    if errors:
        return False, "; ".join(errors)
    return True, f"All overdue invoices for {target_name} (highest combined overdue total) are voided"
