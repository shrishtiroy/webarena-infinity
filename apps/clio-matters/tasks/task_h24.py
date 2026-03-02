import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # "Opened before January 2025" means openDate < 2025-01-01
    cutoff_date = "2025-01-01"

    # Known PI matters at Intake (stage_1_1) opened before 2025-01-01:
    # matter_10 (2024-11-25), matter_11 (2024-12-12)
    expected_closed_ids = ["matter_10", "matter_11"]

    # PI matters at Intake opened in 2025 or later (should NOT be closed):
    # matter_12 (2025-02-05), matter_18 (2025-02-22), matter_22 (2025-02-10),
    # matter_23 (2025-02-28), matter_27 (2025-03-01)
    should_not_close_ids = ["matter_12", "matter_18", "matter_22", "matter_23", "matter_27"]

    matters_by_id = {m["id"]: m for m in state.get("matters", [])}

    closed_count = 0
    for mid in expected_closed_ids:
        matter = matters_by_id.get(mid)
        if matter is None:
            deleted = next(
                (dm for dm in state.get("deletedMatters", []) if dm.get("id") == mid),
                None
            )
            if deleted:
                errors.append(f"Matter {mid} was deleted instead of closed.")
            else:
                errors.append(f"Matter {mid} not found in state.")
            continue

        if matter.get("status") != "closed":
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}', opened {matter.get('openDate')}) "
                f"has status '{matter.get('status')}', expected 'closed'."
            )
        else:
            closed_count += 1

        if not matter.get("closedDate"):
            errors.append(f"Matter {mid} has no closedDate set.")

    # Verify newer matters were NOT closed
    for mid in should_not_close_ids:
        matter = matters_by_id.get(mid)
        if matter and matter.get("status") == "closed":
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}', opened {matter.get('openDate')}) "
                f"should NOT have been closed (opened in 2025 or later)."
            )

    if closed_count < 2:
        errors.append(
            f"Only {closed_count} of the expected PI Intake matters opened before 2025 were closed."
        )

    if errors:
        return False, "PI Intake matters not closed correctly. " + " | ".join(errors)

    return True, (
        f"All {closed_count} Personal Injury matters at Intake stage opened before "
        f"January 2025 have been closed."
    )
