import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check Maritime Law practice area exists
    maritime = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("name") == "Maritime Law"),
        None,
    )
    if not maritime:
        return False, "Maritime Law practice area not found."

    # Check 4 stages exist
    stages = state.get("matterStages", {}).get(maritime["id"], [])
    expected_stages = ["Case Intake", "Investigation", "Arbitration", "Settlement"]
    stage_names = [s.get("name") for s in sorted(stages, key=lambda s: s.get("order", 0))]

    errors = []
    for exp in expected_stages:
        if exp not in stage_names:
            errors.append(f"Stage '{exp}' not found in Maritime Law.")

    # Check Kowalski is in Maritime Law at Investigation stage
    kowalski = next(
        (m for m in state.get("matters", [])
         if "Kowalski" in (m.get("description") or "")),
        None,
    )
    if not kowalski:
        errors.append("Kowalski matter not found.")
    else:
        if kowalski.get("practiceAreaId") != maritime["id"]:
            errors.append(
                f"Kowalski practice area is '{kowalski.get('practiceAreaId')}', "
                f"expected '{maritime['id']}' (Maritime Law)."
            )
        investigation = next(
            (s for s in stages if s.get("name") == "Investigation"),
            None,
        )
        if investigation and kowalski.get("matterStageId") != investigation["id"]:
            errors.append(
                f"Kowalski stage is '{kowalski.get('matterStageId')}', "
                f"expected '{investigation['id']}' (Investigation)."
            )

    if errors:
        return False, " ".join(errors)

    return True, "Maritime Law created with 4 stages, Kowalski moved to Investigation."
