import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    real_estate = None
    for pa in practice_areas:
        if pa.get("name") == "Real Estate":
            real_estate = pa
            break

    if real_estate is None:
        return False, (
            f"Practice area 'Real Estate' not found. "
            f"Existing practice areas: {[pa.get('name') for pa in practice_areas]}"
        )

    stages = real_estate.get("stages", [])
    stage_names = [s.get("name") for s in stages]

    if "Closing" in stage_names:
        return False, (
            f"Stage 'Closing' still exists in 'Real Estate' practice area but should have been removed. "
            f"Current stages: {stage_names}"
        )

    return True, "Stage 'Closing' has been successfully removed from 'Real Estate' practice area."
