import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update phone to '+64 800 100 200' for every contact whose total
    outstanding balance exceeds $50,000."""
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
    expected_phone = "+64 800 100 200"

    # Compute outstanding balance per contact
    balances = {}
    for inv in invoices:
        if inv.get("status") in ("awaiting_payment", "overdue"):
            cid = inv.get("contactId")
            balances[cid] = balances.get(cid, 0) + (inv.get("amountDue") or 0)

    # Known contacts with balance > $50k:
    # Meridian Health Clinic, Bloom & Branch Florists, Pinnacle Construction Co,
    # Green Valley Organics, Hamilton Plumbing Services,
    # Summit Financial Advisors, Velocity Sports Equipment
    expected_ids = set()
    for cid, bal in balances.items():
        if bal > 50000:
            expected_ids.add(cid)

    if len(expected_ids) < 5:
        errors.append(f"Only {len(expected_ids)} contacts have balance > $50k, expected at least 5")

    for cid in expected_ids:
        contact = next((c for c in contacts if c.get("id") == cid), None)
        if contact is None:
            errors.append(f"Contact {cid} not found")
            continue
        phone = (contact.get("phone") or "").strip()
        name = contact.get("name", cid)
        if phone != expected_phone:
            errors.append(f"'{name}' phone is '{phone}', expected '{expected_phone}'")

    # Contacts with balance <= $50k should NOT be updated
    for c in contacts:
        cid = c.get("id")
        bal = balances.get(cid, 0)
        if bal <= 50000 and (c.get("phone") or "").strip() == expected_phone:
            errors.append(f"'{c.get('name')}' (balance ${bal:.2f}) should NOT have been updated")

    if errors:
        return False, "; ".join(errors)
    return True, f"Phone updated for all {len(expected_ids)} contacts with outstanding balance > $50k"
