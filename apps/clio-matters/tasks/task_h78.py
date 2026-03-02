import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Estate Planning (pa_7) stages:
    # stage_7_1 = Initial Consultation -> should become stage_7_2 (Document Preparation)
    # stage_7_2 = Document Preparation -> should become stage_7_3 (Execution)
    # stage_7_3 = Execution -> unchanged

    # Known seed open EP matters:
    # matter_82: stage_7_1 -> should be stage_7_2
    # matter_85: stage_7_1 -> should be stage_7_2
    # matter_86: stage_7_1 -> should be stage_7_2
    # matter_81: stage_7_2 -> should be stage_7_3
    # matter_83: stage_7_2 -> should be stage_7_3
    # matter_117: stage_7_2 -> should be stage_7_3

    expected = {
        "matter_82": "stage_7_2",
        "matter_85": "stage_7_2",
        "matter_86": "stage_7_2",
        "matter_81": "stage_7_3",
        "matter_83": "stage_7_3",
        "matter_117": "stage_7_3",
    }

    for mid, expected_stage in expected.items():
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("stageId") != expected_stage:
            errors.append(
                f"{m.get('description', mid)} stageId is '{m.get('stageId')}', "
                f"expected '{expected_stage}'."
            )

    if errors:
        return False, "Estate Planning stage advancement not correct. " + " | ".join(errors)

    return True, (
        "All open Estate Planning matters correctly advanced: "
        "Initial Consultation matters moved to Document Preparation, "
        "Document Preparation matters moved to Execution."
    )
