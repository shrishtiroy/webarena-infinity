import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    board = next((b for b in state["boards"] if b["name"] == "Development Board"), None)
    if not board:
        return False, "Development Board not found."

    review_list = next((lst for lst in board["lists"] if lst["title"] == "Review"), None)
    if review_list:
        return False, "Review list still exists on Development Board."

    return True, "Review list removed from Development Board."
