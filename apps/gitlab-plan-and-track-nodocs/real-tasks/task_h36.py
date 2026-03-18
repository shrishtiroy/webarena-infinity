import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Milestone 'Security Hardening' should exist
    ms = next((m for m in state["milestones"] if m.get("title") == "Security Hardening"), None)
    if ms is None:
        return False, "Milestone 'Security Hardening' not found."
    if ms.get("dueDate") != "2026-06-30":
        return False, f"Milestone dueDate is '{ms.get('dueDate')}', expected '2026-06-30'."

    ms_id = ms["id"]

    # Open confidential issues #46, #57, #58, #59 should be in this milestone
    for issue_id in [46, 57, 58, 59]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue.get("milestoneId") != ms_id:
            return False, f"Issue #{issue_id} milestoneId is {issue.get('milestoneId')}, expected {ms_id} (Security Hardening)."

    return True, "Milestone 'Security Hardening' created and all confidential issues moved into it."
