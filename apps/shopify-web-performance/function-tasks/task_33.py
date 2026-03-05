import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    target = None
    for rec in recommendations:
        if rec.get("title") == "Evaluate Privy pop-up timing":
            target = rec
            break

    if target is None:
        return False, "Recommendation 'Evaluate Privy pop-up timing' not found in state."

    if target.get("status") != "resolved":
        return False, f"Recommendation status is '{target.get('status')}', expected 'resolved'."

    return True, "Recommendation 'Evaluate Privy pop-up timing' is correctly resolved."
