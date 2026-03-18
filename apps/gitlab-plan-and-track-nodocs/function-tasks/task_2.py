import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [i for i in state["issues"] if i["title"] == "Production API timeout errors"]
    if not match:
        return False, "Issue 'Production API timeout errors' not found."

    issue = match[0]
    if issue["type"] != "incident":
        return False, f"Expected type 'incident', got '{issue['type']}'."

    return True, "Incident 'Production API timeout errors' created successfully."
