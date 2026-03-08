import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez matter not found."

    # Find bill with highest balance owed
    best_bill = None
    best_balance = -1
    for p in rodriguez.get("medicalProviders", []):
        for b in p.get("medicalBills", []):
            bal = b.get("balanceOwed", 0)
            if bal > best_balance:
                best_balance = bal
                best_bill = b

    if not best_bill:
        return False, "No medical bills found on Rodriguez case."

    comments = best_bill.get("comments", [])
    expected_text = "Priority collection \u2014 escalate to senior partner"
    has_comment = any(c.get("text") == expected_text for c in comments)

    if not has_comment:
        return False, (
            f"Comment not found on bill '{best_bill.get('fileName')}' "
            f"(highest balance: ${best_balance:,.0f}). "
            f"Expected: '{expected_text}'."
        )

    return True, (
        f"Comment added to '{best_bill.get('fileName')}' "
        f"(highest balance: ${best_balance:,.0f})."
    )
