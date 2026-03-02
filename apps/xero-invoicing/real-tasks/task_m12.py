import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    repeating = state.get("repeatingInvoices", [])
    target = None
    for inv in repeating:
        if inv.get("id") == "rep_003":
            target = inv
            break

    if target is None:
        return False, "Could not find repeating invoice with id 'rep_003'."

    reference = target.get("reference", "")
    if reference != "Cascade monthly license":
        return False, f"Expected reference 'Cascade monthly license' on rep_003, but found '{reference}'."

    return True, "Repeating invoice rep_003 has reference 'Cascade monthly license'."
