import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check Personal Injury (pa_1) has Emergency Filing stage
    pi = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("id") == "pa_1" or pa.get("name") == "Personal Injury"),
        None,
    )
    if pi is None:
        return False, "Personal Injury practice area not found."

    pi_stages = [s["name"] for s in pi.get("stages", [])]
    if not any("emergency filing" == s.lower() for s in pi_stages):
        errors.append(
            f"Stage 'Emergency Filing' not found in Personal Injury. Stages: {pi_stages}."
        )

    # Check Medical Malpractice (pa_12) has Emergency Filing stage
    mm = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("id") == "pa_12" or pa.get("name") == "Medical Malpractice"),
        None,
    )
    if mm is None:
        return False, "Medical Malpractice practice area not found."

    mm_stages = [s["name"] for s in mm.get("stages", [])]
    if not any("emergency filing" == s.lower() for s in mm_stages):
        errors.append(
            f"Stage 'Emergency Filing' not found in Medical Malpractice. Stages: {mm_stages}."
        )

    if errors:
        return False, " | ".join(errors)

    return True, (
        "Emergency Filing stage correctly added to both Personal Injury "
        "and Medical Malpractice practice areas."
    )
