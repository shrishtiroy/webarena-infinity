import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    stages = state.get("matterStages", {})

    # Family Law is pa_003
    fl_stages = stages.get("pa_003", [])
    stage_names = [s.get("name", "") for s in fl_stages]

    errors = []

    if "Emergency Orders" not in stage_names:
        errors.append(f"'Emergency Orders' stage not found in Family Law stages. Found: {stage_names}")

    if "Property Division" not in stage_names:
        errors.append(f"'Property Division' stage not found in Family Law stages. Found: {stage_names}")

    if errors:
        return False, "; ".join(errors)

    return True, "Both 'Emergency Orders' and 'Property Division' stages added to Family Law practice area."
