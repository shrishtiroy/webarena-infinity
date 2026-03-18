import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    board = next((b for b in state["boards"] if b.get("name") == "Development Board"), None)
    if board is None:
        return False, "Development Board not found."

    lists = board.get("lists", [])

    # To Do (labelId 15) and Done (labelId 18) should be removed
    for label_id, name in [(15, "To Do"), (18, "Done")]:
        if any(l.get("labelId") == label_id for l in lists):
            return False, f"'{name}' list (labelId {label_id}) still exists on Development Board."

    # bug (labelId 1) and security (labelId 5) lists should exist
    for label_id, name in [(1, "bug"), (5, "security")]:
        if not any(l.get("labelId") == label_id for l in lists):
            return False, f"No list for '{name}' label (labelId {label_id}) found on Development Board."

    return True, "To Do and Done lists removed; bug and security lists added to Development Board."
