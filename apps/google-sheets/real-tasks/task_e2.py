import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check that a sheet named "Revenue" exists
    sheet_names = [s["name"] for s in state["sheets"]]
    if "Revenue" in sheet_names:
        return True, "Sheet named 'Revenue' exists."
    return False, f"No sheet named 'Revenue' found. Current sheet names: {sheet_names}."
