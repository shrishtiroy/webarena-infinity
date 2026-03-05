import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settlements = state.get("settlements", {})
    matter_21_settlement = settlements.get("matter_21", {})
    recoveries = matter_21_settlement.get("recoveries", [])

    matching = [r for r in recoveries if r.get("id") == "rec_3" or "SFMTA" in r.get("sourceName", "")]
    if not matching:
        return False, "Recovery with id 'rec_3' or sourceName containing 'SFMTA' not found in matter_21 settlements."

    recovery = matching[0]
    amount = recovery.get("amount")
    if amount != 55000:
        return False, f"Expected recovery amount 55000, got {amount}."

    return True, "Recovery on matter_21 (SFMTA Claims Division) has been updated to amount 55000."
