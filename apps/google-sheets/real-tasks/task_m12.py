import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sales_sheet = None
    for s in state["sheets"]:
        if s["name"] == "Sales":
            sales_sheet = s
            break
    if sales_sheet is None:
        return False, f"Sales sheet not found. Sheet names: {[s['name'] for s in state['sheets']]}"
    charts = sales_sheet.get("charts", [])
    for c in charts:
        if c.get("type") == "line" and c.get("title") == "January Sales":
            return True, "Line chart 'January Sales' found on Sales sheet."
    return False, f"No matching line chart with title 'January Sales' found. Charts: {[{'type': c.get('type'), 'title': c.get('title')} for c in charts]}"
