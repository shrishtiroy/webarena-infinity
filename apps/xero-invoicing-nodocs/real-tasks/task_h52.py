import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Enable late penalties at 5% daily, change company name, and send all
    awaiting approval invoices."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    settings = state.get("settings", {})
    errors = []

    # Check settings
    if not settings.get("latePenaltyEnabled"):
        errors.append("latePenaltyEnabled is not True")
    if abs((settings.get("latePenaltyRate") or 0) - 5) > 0.01:
        errors.append(f"latePenaltyRate is {settings.get('latePenaltyRate')}, expected 5")
    if settings.get("latePenaltyFrequency") != "daily":
        errors.append(f"latePenaltyFrequency is '{settings.get('latePenaltyFrequency')}', expected 'daily'")
    if settings.get("companyName") != "Kiwi Professional Services Ltd":
        errors.append(f"companyName is '{settings.get('companyName')}', expected 'Kiwi Professional Services Ltd'")

    # No awaiting_approval invoices should remain
    still_aa = [inv for inv in invoices if inv.get("status") == "awaiting_approval"]
    if still_aa:
        nums = [inv.get("invoiceNumber") for inv in still_aa]
        errors.append(f"Awaiting approval invoices still exist: {nums}")

    # Known AA invoices should now be awaiting_payment with sentAt
    expected_sent = [
        "INV-0008", "INV-0017", "INV-0032", "INV-0038", "INV-0045",
        "INV-0056", "INV-0066", "INV-0077", "INV-0111", "INV-0112",
    ]
    for inv_num in expected_sent:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "awaiting_payment":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'")
        if not inv.get("sentAt"):
            errors.append(f"{inv_num} has no sentAt")

    if errors:
        return False, "; ".join(errors)
    return True, "Late penalties enabled at 5% daily, company renamed, and all AA invoices sent"
