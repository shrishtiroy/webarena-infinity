import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    rec = next((r for r in recommendations if r.get("title") == "Optimize large hero images on homepage"), None)
    if rec is None:
        return False, "Recommendation 'Optimize large hero images on homepage' not found in recommendations list."

    if rec.get("status") != "resolved":
        return False, f"Expected recommendation status to be 'resolved', but got '{rec.get('status')}'."

    return True, "Hero image optimization recommendation has been marked as resolved (status=resolved)."
