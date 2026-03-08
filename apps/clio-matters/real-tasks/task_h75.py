import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    reeves_contact = next(
        (c for c in state.get("contacts", [])
         if "Reeves" in (c.get("lastName") or "")),
        None,
    )
    if not reeves_contact:
        return False, "Dr. Amanda Reeves contact not found."

    reeves_provider = next(
        (p for p in rodriguez.get("medicalProviders", [])
         if p.get("contactId") == reeves_contact["id"]),
        None,
    )
    if not reeves_provider:
        return False, "Dr. Reeves not found as provider on Rodriguez case."

    bill = next(
        (b for b in reeves_provider.get("medicalBills", [])
         if b.get("fileName") == "Reeves_Evaluation.pdf"),
        None,
    )
    if not bill:
        return False, "Bill 'Reeves_Evaluation.pdf' not found on Dr. Reeves provider."

    errors = []
    if bill.get("billAmount") != 5000:
        errors.append(f"Bill amount is {bill.get('billAmount')}, expected 5000.")
    if bill.get("adjustment") != 500:
        errors.append(f"Adjustment is {bill.get('adjustment')}, expected 500.")
    if bill.get("balanceOwed") != 4500:
        errors.append(f"Balance owed is {bill.get('balanceOwed')}, expected 4500.")
    if bill.get("balanceIsOutstanding") is not True:
        errors.append(f"Balance outstanding flag is {bill.get('balanceIsOutstanding')}, expected True.")

    if errors:
        return False, " ".join(errors)

    return True, "Reeves_Evaluation.pdf bill added with correct amounts and outstanding flag."
