import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Identify which PI Investigation matters had damages in seed
    # We check current state: matters that were at Investigation and open
    # should now be at Demand (if they had damages) or pending (if not)
    damages = state.get("damages", [])
    damage_matter_ids = set(d.get("matterId") for d in damages)

    # Known seed: open PI matters at Investigation stage
    # matter_2 (Johnson v. Whole Foods): has damages -> should be at Demand
    # matter_5 (Doyle v. Summit): has damages -> should be at Demand
    # matter_8 (Mills v. Rodriguez): has damages -> should be at Demand
    # matter_16 (Patterson Workers Comp): no damages -> should be pending
    # matter_20 (Johnson v. Target): no damages -> should be pending
    # matter_26 (Mills v. State of CA): no damages -> should be pending

    expected_demand = ["matter_2", "matter_5", "matter_8"]
    expected_pending = ["matter_16", "matter_20", "matter_26"]

    for mid in expected_demand:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("stageId") != "stage_1_3":
            errors.append(
                f"{m.get('description', mid)} should be at Demand (stage_1_3) "
                f"since it has damages, but stageId is '{m.get('stageId')}'."
            )

    for mid in expected_pending:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found.")
            continue
        if m.get("status") != "pending":
            errors.append(
                f"{m.get('description', mid)} should be pending "
                f"since it has no damages, but status is '{m.get('status')}'."
            )

    if errors:
        return False, "PI Investigation matters not handled correctly. " + " | ".join(errors)

    return True, (
        "All open PI Investigation matters correctly handled: "
        "matters with damages advanced to Demand, matters without damages marked pending."
    )
