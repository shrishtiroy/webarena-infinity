import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    board = next((b for b in state["boards"] if b["name"] == "Development Board"), None)
    if not board:
        return False, "Development Board not found."

    tech_debt = next((l for l in state["labels"] if l["name"] == "tech-debt"), None)
    if not tech_debt:
        return False, "Label 'tech-debt' not found."

    td_list = next((lst for lst in board["lists"] if lst.get("labelId") == tech_debt["id"]), None)
    if not td_list:
        return False, "No list for 'tech-debt' label found on Development Board."

    return True, "List for 'tech-debt' added to Development Board."
