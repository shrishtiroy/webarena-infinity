import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    re_pa_id = "pa_4"

    # Known pending RE matters in seed: matter_56, matter_60, matter_61
    expected_closed = ["matter_56", "matter_60", "matter_61"]

    # Known open RE matters at Due Diligence (stage_4_1) in seed:
    # matter_58, matter_59, matter_62
    expected_moved = ["matter_58", "matter_59", "matter_62"]

    matters_by_id = {m["id"]: m for m in state.get("matters", [])}

    # Check pending matters were closed
    for mid in expected_closed:
        matter = matters_by_id.get(mid)
        if matter is None:
            errors.append(f"Matter {mid} not found.")
            continue
        if matter.get("status") != "closed":
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}') has status "
                f"'{matter.get('status')}', expected 'closed' (was pending)."
            )

    # Check Due Diligence matters were moved to Contract Review (stage_4_2)
    for mid in expected_moved:
        matter = matters_by_id.get(mid)
        if matter is None:
            errors.append(f"Matter {mid} not found.")
            continue
        if matter.get("stageId") != "stage_4_2":
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}') has stageId "
                f"'{matter.get('stageId')}', expected 'stage_4_2' (Contract Review)."
            )

    # Ensure no pending RE matters remain
    remaining_pending = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == re_pa_id and m.get("status") == "pending"
    ]
    if remaining_pending:
        leftover = [f"{m['id']}" for m in remaining_pending]
        errors.append(f"Pending Real Estate matters still exist: {leftover}.")

    # Ensure no open RE matters at Due Diligence remain
    remaining_dd = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == re_pa_id
        and m.get("status") == "open"
        and m.get("stageId") == "stage_4_1"
    ]
    if remaining_dd:
        leftover = [f"{m['id']}" for m in remaining_dd]
        errors.append(f"Open Real Estate matters at Due Diligence still exist: {leftover}.")

    if errors:
        return False, "Real Estate matters not handled correctly. " + " | ".join(errors)

    return True, (
        "All pending Real Estate matters closed and all open Due Diligence "
        "matters moved to Contract Review."
    )
