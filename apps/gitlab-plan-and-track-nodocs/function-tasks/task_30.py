import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    label = next((l for l in state["labels"] if l["name"] == "needs-triage"), None)
    if not label:
        return False, "Label 'needs-triage' not found."

    expected = "Requires initial assessment, categorization, and priority assignment"
    if label["description"] != expected:
        return False, f"Expected description '{expected}', got '{label['description']}'."

    return True, "Label 'needs-triage' description updated."
