import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    board = next((b for b in state["boards"] if b["name"] == "Bug Triage Board"), None)
    if not board:
        return False, "Bug Triage Board not found."

    triage = next((l for l in state["labels"] if l["name"] == "needs-triage"), None)
    if not triage:
        return False, "Label 'needs-triage' not found."

    triage_list = next((lst for lst in board["lists"] if lst.get("labelId") == triage["id"]), None)
    if not triage_list:
        return False, "No list for 'needs-triage' label found on Bug Triage Board."

    return True, "List for 'needs-triage' added to Bug Triage Board."
