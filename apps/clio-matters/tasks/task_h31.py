import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check Securities Law practice area exists with correct stages
    sec_pa = next(
        (pa for pa in state.get("practiceAreas", [])
         if "securities" in pa.get("name", "").lower()),
        None
    )

    if sec_pa is None:
        return False, "Securities Law practice area not found."

    sec_pa_id = sec_pa["id"]
    stages = sec_pa.get("stages", [])
    stage_names = [s.get("name", "").lower() for s in stages]

    expected_stages = ["investigation", "sec filing", "litigation"]
    for expected in expected_stages:
        if not any(expected in sn for sn in stage_names):
            errors.append(f"Stage '{expected}' not found in Securities Law. Stages: {stage_names}.")

    # Find Franklin securities fraud matter (matter_47)
    franklin = next(
        (m for m in state.get("matters", [])
         if "franklin" in m.get("description", "").lower()
         and ("securities" in m.get("description", "").lower()
              or "fraud" in m.get("description", "").lower())),
        None
    )

    if franklin is None:
        errors.append("Could not find Franklin securities fraud matter.")
    else:
        # Check practice area changed to Securities Law
        if franklin.get("practiceAreaId") != sec_pa_id:
            errors.append(
                f"Franklin matter practiceAreaId is '{franklin.get('practiceAreaId')}', "
                f"expected '{sec_pa_id}' (Securities Law)."
            )

        # Check stage is SEC Filing
        sec_filing_stage = next(
            (s for s in stages if "sec filing" in s.get("name", "").lower()),
            None
        )
        if sec_filing_stage and franklin.get("stageId") != sec_filing_stage["id"]:
            errors.append(
                f"Franklin matter stageId is '{franklin.get('stageId')}', "
                f"expected '{sec_filing_stage['id']}' (SEC Filing)."
            )

    if errors:
        return False, "Securities Law setup not complete. " + " | ".join(errors)

    return True, (
        f"Securities Law practice area created with stages {[s['name'] for s in stages]}. "
        f"Franklin matter moved to {sec_pa_id} at SEC Filing stage."
    )
