import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    damages = state.get("damages", [])
    target = None
    for d in damages:
        if d.get("matterId") == "matter_1" and d.get("name", "").lower() == "pain and suffering":
            target = d
            break

    if target is None:
        return False, "Damage 'Pain and Suffering' on matter_1 not found."

    amount = target.get("amount")
    if amount != 200000:
        return False, f"Damage 'Pain and Suffering' amount is {amount}, expected 200000."

    return True, "Damage 'Pain and Suffering' on matter_1 correctly has amount 200000."
