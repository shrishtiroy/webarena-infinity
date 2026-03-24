import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    charts = sheet.get("charts", [])
    for c in charts:
        if c.get("type") == "scatter" and c.get("title") == "Price vs Quantity":
            return True, "Scatter chart 'Price vs Quantity' created."
    return False, f"No matching chart. Charts: {[c.get('title') for c in charts]}"
