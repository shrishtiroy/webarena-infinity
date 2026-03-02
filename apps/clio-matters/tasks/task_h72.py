import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find open PI matters at Litigation stage (stage_1_4)
    pi_litigation = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == "pa_1"
        and m.get("stageId") == "stage_1_5"  # Should have been moved to Settlement/Trial
        and m.get("status") == "open"
        and m.get("openDate")
    ]

    # Also check matters still at Litigation in case the move didn't happen
    still_at_lit = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == "pa_1"
        and m.get("stageId") == "stage_1_4"
        and m.get("status") == "open"
        and m.get("openDate")
    ]

    # The earliest-opened Litigation matter should now be at Settlement/Trial
    # In seed: matter_4 (2024-04-20) and matter_7 (2024-07-22)
    # matter_4 is earlier, should be at stage_1_5

    # Find the matter that was originally at Litigation and is earliest
    all_candidates = pi_litigation + still_at_lit
    if not all_candidates:
        return False, "No PI matters found at Litigation or Settlement/Trial stage."

    earliest = min(all_candidates, key=lambda m: m.get("openDate", "9999"))

    # Check it was moved to Settlement/Trial
    if earliest.get("stageId") != "stage_1_5":
        errors.append(
            f"{earliest.get('description')} (opened {earliest.get('openDate')}) "
            f"is at stage '{earliest.get('stageId')}', expected 'stage_1_5' (Settlement/Trial)."
        )

    # Check settlement has recovery ~$150,000
    matter_id = earliest["id"]
    settlement = state.get("settlements", {}).get(matter_id, {})
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 150000) < 15000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(
            f"No recovery ~$150,000 found for {matter_id}. Amounts: {amounts}."
        )

    if errors:
        return False, (
            "Earliest PI Litigation matter not updated correctly. " + " | ".join(errors)
        )

    return True, (
        f"Correctly identified {earliest.get('description')} (opened {earliest.get('openDate')}) "
        f"as the earliest PI Litigation matter. Moved to Settlement/Trial and "
        f"$150,000 recovery added."
    )
