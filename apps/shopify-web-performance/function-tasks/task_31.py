import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    target = None
    for rec in recommendations:
        if rec.get("title") == "Reserve space for Privy pop-up banner":
            target = rec
            break

    if target is None:
        return False, "Recommendation 'Reserve space for Privy pop-up banner' not found in state."

    if target.get("status") != "resolved":
        return False, f"Recommendation status is '{target.get('status')}', expected 'resolved'."

    return True, "Recommendation 'Reserve space for Privy pop-up banner' is correctly resolved."
