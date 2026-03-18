import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [it for it in state["iterations"] if it["title"] == "May 2026"]
    if not match:
        return False, "Iteration 'May 2026' not found."

    iteration = match[0]
    cadence = next((c for c in state["iterationCadences"] if c["title"] == "Monthly Planning"), None)
    if not cadence:
        return False, "Cadence 'Monthly Planning' not found."

    if iteration["cadenceId"] != cadence["id"]:
        return False, f"Expected cadenceId {cadence['id']}, got {iteration['cadenceId']}."
    if iteration["startDate"] != "2026-05-01":
        return False, f"Expected startDate '2026-05-01', got '{iteration['startDate']}'."
    if iteration["endDate"] != "2026-05-31":
        return False, f"Expected endDate '2026-05-31', got '{iteration['endDate']}'."

    return True, "Iteration 'May 2026' created in Monthly Planning cadence."
