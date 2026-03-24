import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    charts = sheet.get("charts", [])
    for c in charts:
        if c.get("type") == "horizontal_bar" and c.get("title") == "Employee Salaries":
            return True, "Horizontal bar chart 'Employee Salaries' created."
    return False, f"No matching chart. Charts: {[c.get('title') for c in charts]}"
