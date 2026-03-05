import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    quotes = state.get("quotes", [])
    target = None
    for q in quotes:
        if q.get("number") == "QU-0025":
            target = q
            break

    if target is None:
        return False, "Could not find quote with number 'QU-0025'."

    title = target.get("title", "")
    if title != "Online Catering Portal":
        return False, f"Expected title 'Online Catering Portal' on QU-0025, but found '{title}'."

    return True, "Quote QU-0025 has title 'Online Catering Portal'."
