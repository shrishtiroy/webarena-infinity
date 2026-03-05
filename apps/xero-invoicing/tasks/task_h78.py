import requests


SEED_INVOICE_IDS = {
    "inv_000", "inv_001", "inv_002", "inv_003", "inv_004", "inv_005",
    "inv_006", "inv_007", "inv_008", "inv_009", "inv_010", "inv_011",
    "inv_012", "inv_013", "inv_014", "inv_015", "inv_016", "inv_017",
    "inv_018", "inv_019", "inv_020", "inv_021", "inv_022", "inv_023",
    "inv_024", "inv_025",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # QU-0029 (Alpha Logistics, con_012) should be accepted and invoiced
    quo = None
    for q in state.get("quotes", []):
        if q.get("number") == "QU-0029":
            quo = q
            break

    if quo is None:
        return False, "Quote QU-0029 not found."

    if quo.get("status") != "accepted":
        return False, (
            f"QU-0029 status is '{quo.get('status')}', expected 'accepted'."
        )

    if quo.get("isInvoiced") is not True:
        return False, "QU-0029 isInvoiced is not True."

    # New invoice for Alpha Logistics (con_012)
    new_inv = None
    for inv in state.get("invoices", []):
        if inv.get("contactId") == "con_012" and inv.get("id") not in SEED_INVOICE_IDS:
            new_inv = inv
            break

    if new_inv is None:
        return False, (
            "No new invoice found for Alpha Logistics International (con_012)."
        )

    # Should be approved (awaiting_payment) with a partial payment
    if new_inv.get("status") != "awaiting_payment":
        return False, (
            f"New invoice status is '{new_inv.get('status')}', expected 'awaiting_payment'."
        )

    payments = new_inv.get("payments", [])
    if not payments:
        return False, "New invoice has no payments. Expected a $5,000 partial payment."

    total_paid = sum(float(p.get("amount", 0)) for p in payments)
    if abs(total_paid - 5000.00) > 50.00:
        return False, (
            f"New invoice total payments = ${total_paid:.2f}, expected ~$5,000."
        )

    amount_due = float(new_inv.get("amountDue", 0))
    if amount_due < 100.00:
        return False, (
            f"New invoice amountDue = ${amount_due:.2f}. Invoice should still have "
            f"an outstanding balance (only $5,000 of ${new_inv.get('total')} paid)."
        )

    return True, (
        f"QU-0029 accepted and invoiced. New invoice '{new_inv.get('number')}' "
        f"for Alpha Logistics approved with $5,000 partial payment recorded."
    )
