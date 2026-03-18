import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Label 'overdue-risk' should exist with color #e74c3c
    label = next((l for l in state["labels"] if l.get("name") == "overdue-risk"), None)
    if label is None:
        return False, "Label 'overdue-risk' not found."
    if label.get("color") != "#e74c3c":
        return False, f"Label 'overdue-risk' color is '{label.get('color')}', expected '#e74c3c'."

    label_id = label["id"]

    # Open v2.0 issues due before 2026-03-25: #31, #33, #35, #41, #104
    expected = [31, 33, 35, 41, 104]
    for issue_id in expected:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if label_id not in issue.get("labelIds", []):
            return False, f"Issue #{issue_id} does not have 'overdue-risk' label (id {label_id})."

    return True, "Label 'overdue-risk' created and applied to all v2.0 issues due before March 25th."
