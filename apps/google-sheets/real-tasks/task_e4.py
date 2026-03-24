import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check that no sheet named "Inventory" exists
    sheet_names = [s["name"] for s in state["sheets"]]
    if "Inventory" not in sheet_names:
        return True, "Inventory sheet has been successfully deleted."
    return False, f"Inventory sheet still exists. Current sheet names: {sheet_names}."
