import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the new task
    task = next((i for i in state["issues"] if i.get("title") == "Security audit for CI pipeline"), None)
    if task is None:
        return False, "Issue with title 'Security audit for CI pipeline' not found."

    if task.get("type") != "task":
        return False, f"Issue type is '{task.get('type')}', expected 'task'."

    # Assigned to Tom Ramirez (6) — same as #53
    if 6 not in task.get("assigneeIds", []):
        return False, f"Tom Ramirez (id 6) not in assigneeIds: {task.get('assigneeIds')}."

    # Labels: security (5) and devops (9)
    if 5 not in task.get("labelIds", []):
        return False, f"Security label (id 5) not in labelIds: {task.get('labelIds')}."
    if 9 not in task.get("labelIds", []):
        return False, f"Devops label (id 9) not in labelIds: {task.get('labelIds')}."

    # Milestone: v2.1 (id 4) — same as #53
    if task.get("milestoneId") != 4:
        return False, f"MilestoneId is {task.get('milestoneId')}, expected 4 (v2.1 — Integrations)."

    # Should be a child of CI/CD Pipeline Modernization epic
    epic = next((e for e in state["epics"] if "CI/CD Pipeline" in e.get("title", "")), None)
    if epic is None:
        return False, "Epic 'CI/CD Pipeline Modernization' not found."
    if task["id"] not in epic.get("childIssueIds", []):
        return False, f"Task (id {task['id']}) not in CI/CD Pipeline Modernization childIssueIds."

    return True, "Task 'Security audit for CI pipeline' created with correct assignee, labels, milestone, and added to CI/CD epic."
