import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Premier Auto Dealers contact by lastName
    contacts = state.get("contacts", [])
    premier_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Premier Auto Dealers"),
        None
    )
    if not premier_contact:
        return False, "Contact 'Premier Auto Dealers' (company) not found in contacts."

    premier_id = premier_contact["id"]
    recoveries = matter.get("settlement", {}).get("recoveries", [])

    # Check that no recovery references Premier Auto Dealers
    premier_recoveries = [r for r in recoveries if r.get("sourceContactId") == premier_id]
    if premier_recoveries:
        return False, (
            f"Recovery from Premier Auto Dealers still exists "
            f"(amount: {premier_recoveries[0].get('amount')}). It should have been removed."
        )

    # Also check that no legalFees reference a recovery from Premier Auto Dealers
    # Since the recovery is deleted, we check if any legalFee has a recoveryId that
    # does not match any existing recovery (orphaned) or specifically matched the old one.
    # We check by seeing if any legalFee references a recoveryId not in current recoveries.
    legal_fees = matter.get("settlement", {}).get("legalFees", [])
    existing_recovery_ids = {r.get("id") for r in recoveries}
    orphaned_fees = [lf for lf in legal_fees if lf.get("recoveryId") not in existing_recovery_ids]
    if orphaned_fees:
        return False, (
            f"Found {len(orphaned_fees)} legal fee(s) referencing non-existent recoveries "
            f"(orphaned recoveryIds: {[lf.get('recoveryId') for lf in orphaned_fees]}). "
            f"Legal fees tied to the deleted Premier Auto Dealers recovery should also be removed."
        )

    return True, (
        "Recovery from Premier Auto Dealers has been removed and no legal fees reference "
        "the deleted recovery."
    )
