import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find PI practice area
    pi_id = None
    for pa in state.get("practiceAreas", []):
        if pa.get("name") == "Personal Injury":
            pi_id = pa.get("id")
            break
    if not pi_id:
        return False, "Personal Injury practice area not found."

    # Build ordered stage list
    stages = state.get("matterStages", {}).get(pi_id, [])
    stages_sorted = sorted(stages, key=lambda s: s.get("order", 0))
    stage_order = {s["id"]: i for i, s in enumerate(stages_sorted)}

    # Find Investigation stage index
    investigation_idx = None
    for i, s in enumerate(stages_sorted):
        if s.get("name") == "Investigation":
            investigation_idx = i
            break
    if investigation_idx is None:
        return False, "Investigation stage not found in PI stages."

    # Expected: open PI cases past Investigation should each advance one stage
    # Seed: Rodriguez at Discovery(5)→Mediation(6), Foster at Negotiation(3)→LitFiled(4),
    #        Cruz at DemandLetter(2)→Negotiation(3), Harris at Investigation(1)→stays
    expected_advances = {
        "Rodriguez": ("Mediation", 6),
        "Foster": ("Litigation Filed", 4),
        "Cruz": ("Negotiation", 3),
    }
    should_not_advance = {
        "Harris": ("Investigation", 1),
    }

    errors = []
    for m in state.get("matters", []):
        if m.get("practiceAreaId") != pi_id or m.get("status") != "Open":
            continue
        desc = m.get("description") or ""
        stage_id = m.get("matterStageId")
        current_idx = stage_order.get(stage_id)

        for name, (expected_name, expected_idx) in expected_advances.items():
            if name in desc:
                expected_stage_id = stages_sorted[expected_idx]["id"]
                if stage_id != expected_stage_id:
                    actual_name = next(
                        (s["name"] for s in stages_sorted if s["id"] == stage_id),
                        stage_id,
                    )
                    errors.append(
                        f"{desc}: stage is '{actual_name}', expected '{expected_name}'."
                    )
                break

        for name, (expected_name, expected_idx) in should_not_advance.items():
            if name in desc:
                if current_idx is not None and current_idx > expected_idx:
                    actual_name = next(
                        (s["name"] for s in stages_sorted if s["id"] == stage_id),
                        stage_id,
                    )
                    errors.append(
                        f"{desc}: should not have advanced (at '{actual_name}'), "
                        f"expected to stay at '{expected_name}'."
                    )
                break

    if errors:
        return False, " ".join(errors)

    return True, "All open PI cases past Investigation advanced to next stage."
