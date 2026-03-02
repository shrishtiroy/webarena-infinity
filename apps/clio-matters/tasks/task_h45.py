import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Marcus Williams = user_2
    # Demand or later stages for PI (pa_1): stage_1_3, stage_1_4, stage_1_5
    advanced_stages = {"stage_1_3", "stage_1_4", "stage_1_5"}

    # Known seed: Marcus Williams' open matters (all PA1)
    # At Demand or later -> should go to Robert Jackson (user_8)
    expected_jackson = ["matter_1", "matter_7", "matter_13"]  # stage_1_3, stage_1_4, stage_1_3
    # Others -> should go to Diana Reyes (user_3)
    expected_reyes = ["matter_2", "matter_5", "matter_11", "matter_23", "matter_26"]

    for mid in expected_jackson:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("responsibleAttorneyId") != "user_8":
            errors.append(
                f"{m.get('description', mid)} should be reassigned to Robert Jackson (user_8) "
                f"since it was at Demand or later, but responsibleAttorneyId is "
                f"'{m.get('responsibleAttorneyId')}'."
            )

    for mid in expected_reyes:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("responsibleAttorneyId") != "user_3":
            errors.append(
                f"{m.get('description', mid)} should be reassigned to Diana Reyes (user_3), "
                f"but responsibleAttorneyId is '{m.get('responsibleAttorneyId')}'."
            )

    if errors:
        return False, "Marcus Williams reassignment not done correctly. " + " | ".join(errors)

    return True, (
        "All Marcus Williams open matters correctly reassigned: "
        "Demand+ PI matters to Robert Jackson, others to Diana Reyes."
    )
