import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settlements = state.get("settlements", {})
    matter_1_settlement = settlements.get("matter_1")

    if matter_1_settlement is None:
        return False, "No settlement found for matter_1."

    outstanding_balances = matter_1_settlement.get("outstandingBalances", [])
    target = None
    for ob in outstanding_balances:
        if ob.get("holderContactId") == "contact_66":
            target = ob
            break

    if target is None:
        return False, (
            "No outstanding balance with holderContactId 'contact_66' (Meridian Radiology Associates) "
            f"found in matter_1 settlement. Existing balances: {outstanding_balances}"
        )

    responsibility = target.get("responsibility")
    if responsibility != "client":
        return False, f"Outstanding balance responsibility is '{responsibility}', expected 'client'."

    description = (target.get("description") or "").lower()
    if "radiology" not in description:
        return False, (
            f"Outstanding balance description '{target.get('description')}' does not contain 'radiology'."
        )

    balance_owing = target.get("balanceOwing")
    if balance_owing != 2500:
        return False, f"Outstanding balance balanceOwing is {balance_owing}, expected 2500."

    reduction = target.get("reduction")
    if reduction != 500:
        return False, f"Outstanding balance reduction is {reduction}, expected 500."

    return True, "Outstanding balance from contact_66 (Meridian Radiology Associates) correctly added with responsibility 'client', balanceOwing 2500, and reduction 500."
