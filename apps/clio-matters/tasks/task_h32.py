import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # CD matters at Plea Negotiation (stage_3_3) in seed:
    # matter_44 (Thompson Felony assault, open) → should move to Trial (stage_3_4)
    # matter_50 (Thompson DV, pending) → should change to open
    # matter_54 (DeLuca Hit and run, pending) → should change to open

    matters_by_id = {m["id"]: m for m in state.get("matters", [])}

    # matter_44: was open, should now be at Trial stage
    m44 = matters_by_id.get("matter_44")
    if m44 is None:
        errors.append("matter_44 (Thompson Felony assault) not found.")
    else:
        if m44.get("stageId") != "stage_3_4":
            errors.append(
                f"matter_44 (Thompson Felony assault) stageId is '{m44.get('stageId')}', "
                f"expected 'stage_3_4' (Trial). Was open at Plea Negotiation, should move to Trial."
            )

    # matter_50: was pending, should now be open
    m50 = matters_by_id.get("matter_50")
    if m50 is None:
        errors.append("matter_50 (Thompson DV) not found.")
    else:
        if m50.get("status") != "open":
            errors.append(
                f"matter_50 (Thompson DV) status is '{m50.get('status')}', expected 'open'. "
                f"Was pending at Plea Negotiation, should change to open."
            )

    # matter_54: was pending, should now be open
    m54 = matters_by_id.get("matter_54")
    if m54 is None:
        errors.append("matter_54 (DeLuca Hit and run) not found.")
    else:
        if m54.get("status") != "open":
            errors.append(
                f"matter_54 (DeLuca Hit and run) status is '{m54.get('status')}', expected 'open'. "
                f"Was pending at Plea Negotiation, should change to open."
            )

    if errors:
        return False, "CD Plea Negotiation matters not handled correctly. " + " | ".join(errors)

    return True, (
        "All Criminal Defense matters at Plea Negotiation handled correctly: "
        "open matters moved to Trial, pending matters changed to open."
    )
