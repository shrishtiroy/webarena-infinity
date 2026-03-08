import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    pi = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("name") == "Personal Injury"),
        None,
    )
    if not pi:
        return False, "Personal Injury practice area not found."

    stages = state.get("matterStages", {}).get(pi["id"], [])
    if not stages:
        return False, "No stages found for Personal Injury."
    first_stage = min(stages, key=lambda s: s.get("order", 0))

    # All open PI matters should be at first stage
    errors = []
    checked = 0
    for m in state.get("matters", []):
        if m.get("practiceAreaId") != pi["id"] or m.get("status") != "Open":
            continue
        checked += 1
        if m.get("matterStageId") != first_stage["id"]:
            actual = next(
                (s["name"] for s in stages if s["id"] == m.get("matterStageId")),
                m.get("matterStageId"),
            )
            desc = m.get("description") or m.get("id")
            errors.append(f"'{desc}': stage is '{actual}', expected '{first_stage['name']}'.")

    if checked == 0:
        return False, "No open PI matters found."

    if errors:
        return False, " ".join(errors)

    return True, f"All {checked} open PI matters moved to '{first_stage['name']}'."
