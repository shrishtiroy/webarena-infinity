import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    epic = next((e for e in state["epics"] if e["title"] == "Mobile Responsive Redesign"), None)
    if not epic:
        return False, "Epic 'Mobile Responsive Redesign' not found."

    perf_label = next((l for l in state["labels"] if l["name"] == "performance"), None)
    if not perf_label:
        return False, "Label 'performance' not found."

    if perf_label["id"] not in epic["labels"]:
        return False, f"Label 'performance' (id {perf_label['id']}) not in epic labels: {epic['labels']}."

    return True, "Label 'performance' added to epic 'Mobile Responsive Redesign'."
