import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Known seed: open Employment Law matters
    # Intake (stage_6_1): matter_78, matter_79, matter_110 -> should move to EEOC (stage_6_2)
    # Negotiation (stage_6_3): matter_73, matter_80 -> should move to Litigation (stage_6_4)
    # Others should be unchanged:
    # matter_74 (stage_6_4, Litigation) -> stay
    # matter_75 (stage_6_2, EEOC) -> stay

    intake_targets = ["matter_78", "matter_79", "matter_110"]
    negotiation_targets = ["matter_73", "matter_80"]

    for mid in intake_targets:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("stageId") != "stage_6_2":
            errors.append(
                f"{m.get('description', mid)} was at Intake, should be at "
                f"EEOC/Admin Filing (stage_6_2), but stageId is '{m.get('stageId')}'."
            )

    for mid in negotiation_targets:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("stageId") != "stage_6_4":
            errors.append(
                f"{m.get('description', mid)} was at Negotiation, should be at "
                f"Litigation (stage_6_4), but stageId is '{m.get('stageId')}'."
            )

    if errors:
        return False, "Employment Law stage changes not applied correctly. " + " | ".join(errors)

    return True, (
        "All open Employment Law matters correctly updated: "
        "Intake matters moved to EEOC/Admin Filing, "
        "Negotiation matters moved to Litigation."
    )
