import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [l for l in state["labels"] if l["name"] == "breaking-change"]
    if match:
        return False, "Label 'breaking-change' still exists."

    return True, "Label 'breaking-change' deleted."
