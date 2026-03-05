import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settlements = state.get("settlements", {})
    matter_3_settlement = settlements.get("matter_3")

    if matter_3_settlement is None:
        return False, "No settlement found for matter_3."

    legal_fees = matter_3_settlement.get("legalFees", [])

    if not legal_fees:
        return False, "No legal fees found in matter_3 settlement."

    target = None
    for lf in legal_fees:
        if lf.get("id") == "lf_1" or lf.get("recoveryId") == "rec_1":
            target = lf
            break

    if target is None:
        target = legal_fees[0]

    rate = target.get("rate")
    if rate != 40:
        return False, f"Legal fee rate is {rate}, expected 40."

    return True, "Legal fee on matter_3 settlement correctly updated to 40% rate."
