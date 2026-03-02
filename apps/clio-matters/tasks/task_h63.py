import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Priya Sharma = user_5
    # Contingency matters -> Marcus Williams (user_2)
    # Other billing -> Robert Jackson (user_8)

    # Known seed: Priya's open matters
    expected_williams = [
        "matter_10", "matter_12", "matter_16", "matter_18", "matter_22", "matter_106",
    ]  # contingency matters
    expected_jackson = [
        "matter_48", "matter_51",
    ]  # hourly and flat_rate matters

    for mid in expected_williams:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("responsibleAttorneyId") != "user_2":
            errors.append(
                f"{m.get('description', mid)} (contingency) should be reassigned to "
                f"Marcus Williams (user_2), but responsibleAttorneyId is "
                f"'{m.get('responsibleAttorneyId')}'."
            )

    for mid in expected_jackson:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("responsibleAttorneyId") != "user_8":
            errors.append(
                f"{m.get('description', mid)} (non-contingency) should be reassigned to "
                f"Robert Jackson (user_8), but responsibleAttorneyId is "
                f"'{m.get('responsibleAttorneyId')}'."
            )

    if errors:
        return False, "Priya Sharma caseload transfer not correct. " + " | ".join(errors)

    return True, (
        "All Priya Sharma open matters correctly reassigned: "
        "contingency matters to Marcus Williams, others to Robert Jackson."
    )
