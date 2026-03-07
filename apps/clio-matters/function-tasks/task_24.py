import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Premier Auto Dealers contact
    contacts = state.get("contacts", [])
    premier_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Premier Auto Dealers"),
        None
    )
    if not premier_contact:
        return False, "Contact 'Premier Auto Dealers' (company) not found in contacts."

    premier_id = premier_contact["id"]

    # Find recoveries from Premier Auto Dealers
    recoveries = matter.get("settlement", {}).get("recoveries", [])
    premier_recovery_ids = {r["id"] for r in recoveries if r.get("sourceContactId") == premier_id}

    # Check legal fees - none should reference a Premier Auto Dealers recovery
    legal_fees = matter.get("settlement", {}).get("legalFees", [])

    # If the recovery itself was deleted, check for orphaned references too
    if premier_recovery_ids:
        matching_fees = [lf for lf in legal_fees if lf.get("recoveryId") in premier_recovery_ids]
        if matching_fees:
            return False, (
                f"Found {len(matching_fees)} legal fee(s) still referencing a Premier Auto Dealers "
                f"recovery. They should have been removed."
            )

    # Also check: even if recovery was deleted, there may be fees with old recoveryId
    # that no longer exists. We consider the task passing as long as no fee references
    # a recovery that was from Premier Auto Dealers. If recovery is gone, any orphaned
    # fee referencing it is also a problem (handled by task_21), but here we just check
    # that no fee explicitly ties to Premier Auto Dealers.
    # If premier_recovery_ids is empty (recovery already deleted), that's fine - no fees can match.

    return True, "No legal fee references a Premier Auto Dealers recovery."
