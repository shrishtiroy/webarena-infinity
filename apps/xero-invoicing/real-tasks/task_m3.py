import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])

    # Find the original invoice
    original = None
    for i in invoices:
        if i.get("number") == "INV-0046":
            original = i
            break

    if original is None:
        return False, "Original invoice INV-0046 not found."

    original_contact = original.get("contactId")
    if original_contact != "con_005":
        return False, f"Original invoice INV-0046 contactId is '{original_contact}', expected 'con_005'."

    # Find a new invoice (not INV-0046) with the same contactId
    copy_found = None
    for i in invoices:
        if i.get("number") == "INV-0046":
            continue
        if i.get("contactId") == original_contact:
            # Check if it's a draft with line items
            if i.get("status") == "draft" and len(i.get("lineItems", [])) > 0:
                copy_found = i
                break

    if copy_found is None:
        return False, "No new draft invoice found for contactId 'con_005' (Baxter & Associates Legal) with at least one line item."

    return True, f"A copy of invoice INV-0046 was created as '{copy_found.get('number')}' in draft status with {len(copy_found.get('lineItems', []))} line item(s)."
