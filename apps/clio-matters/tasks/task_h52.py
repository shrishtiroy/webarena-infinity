import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Brennan hotel matter
    matter = next(
        (m for m in state.get("matters", [])
         if "brennan" in m.get("description", "").lower()
         and "oceanview" in m.get("description", "").lower()),
        None
    )
    if matter is None:
        return False, "Could not find the Brennan hotel slip-and-fall matter."

    matter_id = matter["id"]

    # Check stage is Investigation (stage_1_2)
    if matter.get("stageId") != "stage_1_2":
        errors.append(
            f"Stage is '{matter.get('stageId')}', expected 'stage_1_2' (Investigation)."
        )

    # Check Judge Assigned custom field (cf_7)
    cf = matter.get("customFields", {})
    judge_val = cf.get("cf_7", "")
    if "rodriguez" not in judge_val.lower():
        errors.append(
            f"Judge Assigned custom field is '{judge_val}', expected 'Hon. Michael Rodriguez'."
        )

    # Check settlement recovery ~$200,000
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 200000) < 20000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$200,000 found. Recovery amounts: {amounts}.")

    if errors:
        return False, "Brennan matter changes not applied correctly. " + " | ".join(errors)

    return True, (
        f"Brennan matter ({matter_id}) correctly updated: "
        f"moved to Investigation, Judge Assigned set, $200,000 recovery added."
    )
