import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [it for it in state["iterations"] if it["title"] == "Sprint 28"]
    if not match:
        return False, "Iteration 'Sprint 28' not found."

    iteration = match[0]
    cadence = next((c for c in state["iterationCadences"] if c["title"] == "Sprint Cycle"), None)
    if not cadence:
        return False, "Cadence 'Sprint Cycle' not found."

    if iteration["cadenceId"] != cadence["id"]:
        return False, f"Expected cadenceId {cadence['id']}, got {iteration['cadenceId']}."
    if iteration["startDate"] != "2026-04-14":
        return False, f"Expected startDate '2026-04-14', got '{iteration['startDate']}'."
    if iteration["endDate"] != "2026-04-27":
        return False, f"Expected endDate '2026-04-27', got '{iteration['endDate']}'."

    return True, "Iteration 'Sprint 28' created in Sprint Cycle cadence."
