import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    damages = state.get("damages", [])
    target = None
    for d in damages:
        if d.get("matterId") == "matter_1" and d.get("name") == "Lost Wages - Q1 2025":
            target = d
            break

    if target is None:
        return False, "Damage 'Lost Wages - Q1 2025' on matter_1 not found."

    amount = target.get("amount")
    if amount != 12500:
        return False, f"Damage 'Lost Wages - Q1 2025' amount is {amount}, expected 12500."

    damage_type = target.get("type")
    if damage_type != "special":
        return False, f"Damage 'Lost Wages - Q1 2025' type is '{damage_type}', expected 'special'."

    return True, "Damage 'Lost Wages - Q1 2025' on matter_1 correctly added with amount 12500 and type 'special'."
