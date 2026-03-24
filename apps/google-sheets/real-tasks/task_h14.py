import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found in state."

    sales = sheets[0]
    charts = sales.get("charts", [])

    found_bar = False
    found_scatter = False

    for chart in charts:
        chart_type = chart.get("type", "")
        chart_title = chart.get("title", "")
        if chart_type == "bar" and chart_title == "Sales Quantities":
            found_bar = True
        if chart_type == "scatter" and chart_title == "Price vs Quantity":
            found_scatter = True

    if not found_bar:
        errors.append("No bar chart with title 'Sales Quantities' found on Sales sheet")
    if not found_scatter:
        errors.append("No scatter chart with title 'Price vs Quantity' found on Sales sheet")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
