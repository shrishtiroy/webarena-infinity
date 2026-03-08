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

    riverside = next(
        (c for c in state.get("contacts", [])
         if "Riverside" in (c.get("lastName") or "")),
        None,
    )
    if not riverside:
        return False, "Riverside Community Credit Union not found."

    # Check lien removed
    liens = rodriguez.get("settlement", {}).get("otherLiens", [])
    riverside_lien = next(
        (lien for lien in liens if lien.get("lienHolderId") == riverside["id"]),
        None,
    )
    if riverside_lien:
        return False, "Riverside CU lien should have been removed but still exists."

    # Check new outstanding balance exists (seed lien amount was $5,000)
    balances = rodriguez.get("settlement", {}).get("outstandingBalances", [])
    new_balance = next(
        (b for b in balances
         if b.get("balanceHolderId") == riverside["id"]
         and "Converted" in (b.get("description") or "")
         and b.get("balanceOwing") == 5000),
        None,
    )
    if not new_balance:
        return False, (
            "New outstanding balance for Riverside CU with amount $5,000 "
            "and description containing 'Converted' not found."
        )

    if new_balance.get("responsibleParty") != "client":
        return False, (
            f"Balance responsible party is '{new_balance.get('responsibleParty')}', "
            f"expected 'client'."
        )

    return True, "Riverside CU lien removed and converted to outstanding balance."
