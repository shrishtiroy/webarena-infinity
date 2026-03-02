import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    marcus_id = "user_2"
    diana_id = "user_3"

    # Known Marcus Williams open PI matters at Investigation (stage_1_2) in seed:
    # matter_2 (Johnson v. Whole Foods), matter_5 (Doyle v. Summit), matter_26 (Mills v. State)
    expected_transferred = ["matter_2", "matter_5", "matter_26"]

    matters_by_id = {m["id"]: m for m in state.get("matters", [])}

    transferred = 0
    for mid in expected_transferred:
        matter = matters_by_id.get(mid)
        if matter is None:
            errors.append(f"Matter {mid} not found in state.")
            continue

        if matter.get("responsibleAttorneyId") != diana_id:
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}') has attorney "
                f"'{matter.get('responsibleAttorneyId')}', expected '{diana_id}' (Diana Reyes)."
            )
        else:
            transferred += 1

        if matter.get("stageId") != "stage_1_3":
            errors.append(
                f"Matter {mid} ('{matter.get('description', '')}') has stageId "
                f"'{matter.get('stageId')}', expected 'stage_1_3' (Demand)."
            )

    # Check no other Marcus PI Investigation matters remain
    remaining = [
        m for m in state.get("matters", [])
        if m.get("responsibleAttorneyId") == marcus_id
        and m.get("practiceAreaId") == "pa_1"
        and m.get("stageId") == "stage_1_2"
        and m.get("status") == "open"
    ]
    if remaining:
        leftover = [f"{m['id']} ('{m.get('description', '')}')" for m in remaining]
        errors.append(
            f"Marcus Williams still has open PI Investigation matters: {leftover}."
        )

    if transferred < 2:
        errors.append(
            f"Only {transferred} of the expected matters were transferred to Diana Reyes."
        )

    if errors:
        return False, "Reassignment not completed correctly. " + " | ".join(errors)

    return True, (
        f"All {transferred} of Marcus Williams' open PI Investigation matters "
        f"reassigned to Diana Reyes and moved to Demand stage."
    )
