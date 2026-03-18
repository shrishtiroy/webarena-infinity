import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [i for i in state["issues"] if i["title"] == "Login form does not validate email format"]
    if not match:
        return False, "Issue 'Login form does not validate email format' not found."

    issue = match[0]
    desc = issue.get("description") or ""
    if "Steps to Reproduce" not in desc:
        return False, "Description does not contain Bug Report template content ('Steps to Reproduce')."

    return True, "Issue created with Bug Report template."
