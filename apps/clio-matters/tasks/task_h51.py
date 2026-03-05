import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []
    cutoff = "2024-06-01"

    # Known seed: open matters opened before June 2024
    # PI (pa_1): matter_1 (2024-03-20), matter_4 (2024-04-20), matter_2 (2024-05-15) -> stage_1_5
    # FL (pa_2): matter_28 (2024-01-12), matter_34 (2024-04-16) -> closed

    pi_targets = ["matter_1", "matter_4", "matter_2"]
    fl_targets = ["matter_28", "matter_34"]

    for mid in pi_targets:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("stageId") != "stage_1_5":
            errors.append(
                f"{m.get('description', mid)} (PI, opened before June 2024) should be at "
                f"Settlement/Trial (stage_1_5), but stageId is '{m.get('stageId')}'."
            )

    for mid in fl_targets:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("status") != "closed":
            errors.append(
                f"{m.get('description', mid)} (FL, opened before June 2024) should be closed, "
                f"but status is '{m.get('status')}'."
            )

    if errors:
        return False, "Date-filtered bulk operation not done correctly. " + " | ".join(errors)

    return True, (
        "All open matters opened before June 2024 correctly handled: "
        "PI matters moved to Settlement/Trial, FL matters closed."
    )
