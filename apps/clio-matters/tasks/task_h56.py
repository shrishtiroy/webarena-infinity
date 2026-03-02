import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Whitfield v. BART matter
    matter = next(
        (m for m in state.get("matters", [])
         if "whitfield" in m.get("description", "").lower()
         and ("bart" in m.get("description", "").lower()
              or "rapid transit" in m.get("description", "").lower()
              or "escalator" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find the Whitfield v. BART escalator injury matter."

    matter_id = matter["id"]

    # Check billing is contingency at ~40%
    billing = matter.get("billing", {})
    method = matter.get("billingMethod", billing.get("method"))
    if method != "contingency":
        errors.append(f"Billing method is '{method}', expected 'contingency'.")
    else:
        cont_fee = billing.get("contingencyFee", {})
        if cont_fee:
            pct = float(cont_fee.get("percentage", 0))
            if abs(pct - 40) > 3:
                errors.append(f"Contingency percentage is {pct}%, expected ~40%.")
        else:
            errors.append("No contingency fee configured.")

    # Check custom fields
    cf = matter.get("customFields", {})
    if cf.get("cf_1") != "SF-2025-PI-1212":
        errors.append(
            f"Court Case Number is '{cf.get('cf_1')}', expected 'SF-2025-PI-1212'."
        )
    judge_val = cf.get("cf_7", "")
    if "patricia chen" not in judge_val.lower():
        errors.append(
            f"Judge Assigned is '{judge_val}', expected 'Hon. Patricia Chen'."
        )

    # Check stage is Investigation (stage_1_2)
    if matter.get("stageId") != "stage_1_2":
        errors.append(
            f"Stage is '{matter.get('stageId')}', expected 'stage_1_2' (Investigation)."
        )

    if errors:
        return False, "Whitfield v. BART changes not applied correctly. " + " | ".join(errors)

    return True, (
        f"Whitfield v. BART ({matter_id}) correctly updated: "
        f"contingency at 40%, Court Case Number and Judge Assigned set, "
        f"moved to Investigation stage."
    )
