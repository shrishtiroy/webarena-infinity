import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    rules = sheet.get("conditionalFormats", [])
    for r in rules:
        if (r.get("range") == "D2:D31" and r.get("type") == "less_than" and
            str(r.get("value")) == "20" and r.get("backgroundColor") == "#ffc7ce"):
            return True, "Conditional format rule added."
    return False, f"No matching rule found. Rules: {rules}"
