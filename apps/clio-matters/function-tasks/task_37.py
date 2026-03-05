import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    personal_injury = None
    for pa in practice_areas:
        if pa.get("name") == "Personal Injury":
            personal_injury = pa
            break

    if personal_injury is None:
        return False, (
            f"Practice area 'Personal Injury' not found. "
            f"Existing practice areas: {[pa.get('name') for pa in practice_areas]}"
        )

    stages = personal_injury.get("stages", [])
    stage_names = [s.get("name") for s in stages]

    if "Case Intake" not in stage_names:
        return False, (
            f"Stage 'Case Intake' not found in 'Personal Injury' practice area. "
            f"Current stages: {stage_names}"
        )

    if "Intake" in stage_names:
        return False, (
            f"Old stage name 'Intake' still exists in 'Personal Injury' practice area. "
            f"It should have been renamed to 'Case Intake'. Current stages: {stage_names}"
        )

    return True, "Stage successfully renamed from 'Intake' to 'Case Intake' in 'Personal Injury' practice area."
