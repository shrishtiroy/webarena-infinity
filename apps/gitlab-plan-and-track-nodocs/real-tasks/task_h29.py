import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    epic = next((e for e in state["epics"] if e.get("title") == "Frontend Bug Fixes"), None)
    if epic is None:
        return False, "Epic 'Frontend Bug Fixes' not found."

    if 1 not in epic.get("labels", []):
        return False, f"Label 'bug' (id 1) not in epic labels: {epic.get('labels')}."

    if 8 not in epic.get("labels", []):
        return False, f"Label 'frontend' (id 8) not in epic labels: {epic.get('labels')}."

    # All open issues with both bug (1) and frontend (8) labels
    expected_children = [28, 31, 37, 67, 72, 78, 97, 110, 117, 120, 127]
    for issue_id in expected_children:
        if issue_id not in epic.get("childIssueIds", []):
            return False, f"Issue #{issue_id} not in epic childIssueIds: {epic.get('childIssueIds')}."

    return True, "Epic 'Frontend Bug Fixes' created with bug+frontend labels and all 11 matching child issues."
