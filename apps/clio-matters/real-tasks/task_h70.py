import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find open matter with outstanding balances (should be Rodriguez)
    target = None
    for m in state.get("matters", []):
        if m.get("status") != "Open":
            continue
        balances = m.get("settlement", {}).get("outstandingBalances", [])
        if balances:
            target = m
            break

    if not target:
        return False, "No open matter with outstanding balances found."

    # Get the balance holder and amount
    balance = target["settlement"]["outstandingBalances"][0]
    holder_id = balance.get("balanceHolderId")
    balance_amount = balance.get("balanceOwing")

    # Check for new lien from that same holder with matching amount
    liens = target.get("settlement", {}).get("otherLiens", [])
    new_lien = None
    for lien in liens:
        if (lien.get("lienHolderId") == holder_id
                and lien.get("amount") == balance_amount
                and "Additional services" in (lien.get("description") or "")):
            new_lien = lien
            break

    if not new_lien:
        return False, (
            f"No lien from outstanding balance holder with amount {balance_amount} "
            f"and description containing 'Additional services' found."
        )

    return True, "Lien added matching outstanding balance holder and amount."
