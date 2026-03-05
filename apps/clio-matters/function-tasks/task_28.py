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

    recoveries = matter_1_settlement.get("recoveries", [])
    target = None
    for r in recoveries:
        source_contact = r.get("sourceContactId", "")
        source_name = (r.get("sourceName") or "").lower()
        if source_contact == "contact_58" or "state farm" in source_name:
            target = r
            break

    if target is None:
        return False, (
            "No recovery from contact_58 (State Farm Insurance) found in matter_1 settlement. "
            f"Existing recoveries: {recoveries}"
        )

    amount = target.get("amount")
    if amount != 150000:
        return False, f"Recovery from State Farm amount is {amount}, expected 150000."

    return True, "Recovery from contact_58 (State Farm Insurance) for $150,000 correctly added to matter_1 settlement."
