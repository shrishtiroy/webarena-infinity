import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find PI practice area
    pi = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("name") == "Personal Injury"),
        None,
    )
    if not pi:
        return False, "Personal Injury practice area not found."

    # Check Arbitration stage exists
    stages = state.get("matterStages", {}).get(pi["id"], [])
    arb_stage = next(
        (s for s in stages if s.get("name") == "Arbitration"),
        None,
    )
    if not arb_stage:
        return False, "Arbitration stage not found in Personal Injury."

    # Check Rodriguez is at Arbitration
    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    if rodriguez.get("matterStageId") != arb_stage["id"]:
        return False, (
            f"Rodriguez stage is '{rodriguez.get('matterStageId')}', "
            f"expected '{arb_stage['id']}' (Arbitration)."
        )

    return True, "Arbitration stage added to PI and Rodriguez moved to it."
