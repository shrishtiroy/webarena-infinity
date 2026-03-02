import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    target = None
    for rec in recommendations:
        if rec.get("title") == "Audit tag manager for unused tags":
            target = rec
            break

    if target is None:
        return False, "Recommendation 'Audit tag manager for unused tags' not found in state."

    if target.get("status") != "open":
        return False, f"Recommendation status is '{target.get('status')}', expected 'open'."

    return True, "Recommendation 'Audit tag manager for unused tags' is correctly reopened to 'open'."
