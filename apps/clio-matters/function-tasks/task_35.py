import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    criminal_defense = None
    for pa in practice_areas:
        if pa.get("name") == "Criminal Defense":
            criminal_defense = pa
            break

    if criminal_defense is None:
        return False, (
            f"Practice area 'Criminal Defense' not found. "
            f"Existing practice areas: {[pa.get('name') for pa in practice_areas]}"
        )

    stages = criminal_defense.get("stages", [])
    stage_names = [s.get("name") for s in stages]

    if "Appeals" not in stage_names:
        return False, (
            f"Stage 'Appeals' not found in 'Criminal Defense' practice area. "
            f"Existing stages: {stage_names}"
        )

    return True, "Practice area 'Criminal Defense' correctly has a stage named 'Appeals'."
