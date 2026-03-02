import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    target = None
    for rec in recommendations:
        if rec.get("title") == "Preload web fonts":
            target = rec
            break

    if target is None:
        return False, "Recommendation 'Preload web fonts' not found in state."

    if target.get("status") != "dismissed":
        return False, f"Recommendation status is '{target.get('status')}', expected 'dismissed'."

    return True, "Recommendation 'Preload web fonts' is correctly dismissed."
