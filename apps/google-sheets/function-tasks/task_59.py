import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    filters = sheet.get("filters", {})
    d_filter = filters.get("D")
    if d_filter and "West" in d_filter.get("hiddenValues", []):
        return True, "Filter set on column D hiding 'West'."
    return False, f"Filters: {filters}"
