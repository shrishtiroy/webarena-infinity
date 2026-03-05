import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    rec = next((r for r in recommendations if r.get("title") == "Audit tag manager for unused tags"), None)
    if rec is None:
        return False, "Recommendation 'Audit tag manager for unused tags' not found in recommendations list."

    if rec.get("status") != "open":
        return False, f"Expected recommendation status to be 'open', but got '{rec.get('status')}'."

    return True, "Recommendation about auditing unused tags has been reopened (status=open)."
