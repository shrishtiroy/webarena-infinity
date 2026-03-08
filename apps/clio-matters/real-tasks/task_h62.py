import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find payer on Rodriguez NM Hospital bill
    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    nm_contact = next(
        (c for c in state.get("contacts", [])
         if "Northwestern" in (c.get("lastName") or "")),
        None,
    )
    if not nm_contact:
        return False, "Northwestern Memorial Hospital contact not found."

    nm_provider = next(
        (p for p in rodriguez.get("medicalProviders", [])
         if p.get("contactId") == nm_contact["id"]),
        None,
    )
    if not nm_provider:
        return False, "NM Hospital not found as provider on Rodriguez."

    nm_bills = nm_provider.get("medicalBills", [])
    if not nm_bills or not nm_bills[0].get("payers"):
        return False, "No payers on NM Hospital bill."
    payer_id = nm_bills[0]["payers"][0]["payerId"]

    # Find highest-paid firm member
    highest = max(state.get("firmUsers", []), key=lambda u: u.get("rate", 0))

    # Find Cruz
    cruz = next(
        (m for m in state.get("matters", [])
         if "Cruz" in (m.get("description") or "") and "Metro Transit" in (m.get("description") or "")),
        None,
    )
    if not cruz:
        return False, "Cruz matter not found."

    # Check recovery
    recovery = next(
        (r for r in cruz.get("settlement", {}).get("recoveries", [])
         if r.get("sourceContactId") == payer_id and r.get("amount") == 60000),
        None,
    )
    if not recovery:
        return False, "No $60,000 recovery from NM Hospital bill payer found on Cruz."

    # Check legal fee
    fee = next(
        (f for f in cruz.get("settlement", {}).get("legalFees", [])
         if f.get("recoveryId") == recovery["id"]),
        None,
    )
    if not fee:
        return False, "No legal fee found for the new recovery on Cruz."

    errors = []
    if fee.get("recipientId") != highest["id"]:
        errors.append(
            f"Fee recipient is '{fee.get('recipientId')}', "
            f"expected '{highest['id']}' ({highest['fullName']})."
        )
    if fee.get("rate") != 30:
        errors.append(f"Fee rate is {fee.get('rate')}%, expected 30%.")

    if errors:
        return False, " ".join(errors)

    return True, "Cruz: recovery from bill payer + legal fee with highest-paid firm member at 30%."
