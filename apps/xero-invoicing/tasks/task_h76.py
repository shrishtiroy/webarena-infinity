import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Overdue invoices (due before 2026-03-02, awaiting_payment) ranked by balance:
    # 1. INV-0047: $18,652.70 (CloudNine)
    # 2. INV-0045: $10,890.00 (Pinnacle, partial payment already)
    # 3. INV-0046: $6,655.00 (Baxter)
    # 4. INV-0051: $6,060.00 (Summit Health)
    # 5. INV-0049: $2,996.00 (Coastal Living)
    target_invoices = {
        "INV-0047": {"seed_paid": 0, "seed_due": 18652.70},
        "INV-0045": {"seed_paid": 4950.00, "seed_due": 10890.00},
        "INV-0046": {"seed_paid": 0, "seed_due": 6655.00},
    }

    for inv_num, expected in target_invoices.items():
        inv = None
        for i in state.get("invoices", []):
            if i.get("number") == inv_num:
                inv = i
                break

        if inv is None:
            return False, f"{inv_num} not found."

        amount_paid = float(inv.get("amountPaid", 0))
        expected_paid = expected["seed_paid"] + 1000.00
        if abs(amount_paid - expected_paid) > 50.00:
            return False, (
                f"{inv_num} amountPaid = ${amount_paid:.2f}, "
                f"expected ~${expected_paid:.2f} (seed + $1,000)."
            )

        amount_due = float(inv.get("amountDue", 0))
        expected_due = expected["seed_due"] - 1000.00
        if abs(amount_due - expected_due) > 50.00:
            return False, (
                f"{inv_num} amountDue = ${amount_due:.2f}, "
                f"expected ~${expected_due:.2f}."
            )

    return True, (
        "$1,000 partial payment recorded on each of the three overdue invoices "
        "with the largest balances: INV-0047, INV-0045, INV-0046."
    )
