import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [l for l in state["labels"] if l["name"] == "environment::staging"]
    if not match:
        return False, "Label 'environment::staging' not found."

    label = match[0]
    if not label.get("scoped"):
        return False, "Label should be scoped but scoped is false."
    if label["color"].lower() != "#5cb85c":
        return False, f"Expected color '#5cb85c', got '{label['color']}'."

    return True, "Scoped label 'environment::staging' created with color #5cb85c."
