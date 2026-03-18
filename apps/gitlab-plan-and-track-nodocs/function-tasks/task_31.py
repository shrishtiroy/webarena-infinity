import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    label = next((l for l in state["labels"] if l["name"] == "bug"), None)
    if not label:
        return False, "Label 'bug' not found."

    if label["color"].lower() != "#e74c3c":
        return False, f"Expected color '#e74c3c', got '{label['color']}'."

    return True, "Label 'bug' color changed to #e74c3c."
