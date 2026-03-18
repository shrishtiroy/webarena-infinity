import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 109), None)
    if not issue:
        return False, "Issue #109 not found."

    tech_debt = next((l for l in state["labels"] if l["name"] == "tech-debt"), None)
    if not tech_debt:
        return False, "Label 'tech-debt' not found."

    if tech_debt["id"] not in issue["labels"]:
        return False, f"Label 'tech-debt' (id {tech_debt['id']}) not in issue labels: {issue['labels']}."

    return True, "Label 'tech-debt' added to issue #109."
