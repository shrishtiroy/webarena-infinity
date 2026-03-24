import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that filter mode is turned on for the Sales sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found in application state."

    sales_sheet = sheets[0]
    filter_mode = sales_sheet.get("filterMode", False)

    if filter_mode is True:
        return True, "Filter mode is enabled on the Sales sheet."

    return False, f"Filter mode is not enabled on the Sales sheet. filterMode = {filter_mode}"
