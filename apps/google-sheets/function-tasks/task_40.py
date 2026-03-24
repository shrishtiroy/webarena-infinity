import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    charts = sheet.get("charts", [])
    for c in charts:
        if c.get("type") == "line" and c.get("title") == "January Sales":
            return True, "Line chart 'January Sales' created."
    return False, f"No matching chart found. Charts: {[c.get('title') for c in charts]}"
