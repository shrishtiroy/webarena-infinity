import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [l for l in state["labels"] if l["name"] == "testing"]
    if not match:
        return False, "Label 'testing' not found."

    label = match[0]
    if label["color"].lower() != "#17a2b8":
        return False, f"Expected color '#17a2b8', got '{label['color']}'."

    return True, "Label 'testing' created with color #17a2b8."
