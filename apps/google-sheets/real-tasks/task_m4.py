import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Insert a bar chart on the Sales sheet using the Quantity column (E1:E41) titled 'Sales Volume'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Sales sheet is at index 0
    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found."

    sales = sheets[0]
    charts = sales.get("charts", [])

    if not charts:
        return False, "No charts found on the Sales sheet."

    for chart in charts:
        chart_type = chart.get("type", "").lower()
        chart_title = chart.get("title", "")

        if chart_type == "bar" and chart_title == "Sales Volume":
            return True, f"Found bar chart titled 'Sales Volume' on the Sales sheet."

    chart_info = [{"type": c.get("type"), "title": c.get("title")} for c in charts]
    return False, (
        f"No bar chart with title 'Sales Volume' found on the Sales sheet. "
        f"Found charts: {chart_info}"
    )
