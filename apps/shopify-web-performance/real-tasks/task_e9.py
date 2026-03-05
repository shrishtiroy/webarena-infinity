import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    rec = next((r for r in recommendations if r.get("title") == "Preload web fonts"), None)
    if rec is None:
        return False, "Recommendation 'Preload web fonts' not found in recommendations list."

    if rec.get("status") != "dismissed":
        return False, f"Expected recommendation status to be 'dismissed', but got '{rec.get('status')}'."

    return True, "Web fonts preloading recommendation has been dismissed (status=dismissed)."
