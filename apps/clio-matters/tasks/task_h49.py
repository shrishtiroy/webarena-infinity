import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the most recently opened PI matter
    pi_matters = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == "pa_1" and m.get("openDate")
    ]
    if not pi_matters:
        return False, "No Personal Injury matters found."

    most_recent = max(pi_matters, key=lambda m: m["openDate"])
    matter_id = most_recent["id"]

    # Check for special damage ~$30,000 for emergency medical treatment
    damages = state.get("damages", [])
    matter_damages = [d for d in damages if d.get("matterId") == matter_id]
    has_damage = any(
        d.get("type") == "special"
        and abs(float(d.get("amount", 0)) - 30000) < 5000
        for d in matter_damages
    )
    if not has_damage:
        existing = [(d.get("name"), d.get("amount"), d.get("type")) for d in matter_damages]
        errors.append(
            f"No special damage ~$30,000 found on {most_recent.get('description')} ({matter_id}). "
            f"Existing damages: {existing}."
        )

    # Check stage is Investigation (stage_1_2)
    if most_recent.get("stageId") != "stage_1_2":
        errors.append(
            f"{most_recent.get('description')} stageId is '{most_recent.get('stageId')}', "
            f"expected 'stage_1_2' (Investigation)."
        )

    if errors:
        return False, (
            f"Most recently opened PI matter ({most_recent.get('description')}, "
            f"opened {most_recent.get('openDate')}) not handled correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"Most recently opened PI matter ({most_recent.get('description')}, "
        f"opened {most_recent.get('openDate')}): $30,000 special damage added "
        f"and moved to Investigation stage."
    )
