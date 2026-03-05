import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Mills v. Rodriguez matter
    matter = next(
        (m for m in state.get("matters", [])
         if "mills" in m.get("description", "").lower()
         and "rodriguez" in m.get("description", "").lower()),
        None
    )
    if matter is None:
        return False, "Could not find the Mills v. Rodriguez motorcycle collision matter."

    matter_id = matter["id"]

    # Check responsible attorney is Diana Reyes (user_3)
    if matter.get("responsibleAttorneyId") != "user_3":
        errors.append(
            f"Responsible attorney is '{matter.get('responsibleAttorneyId')}', "
            f"expected 'user_3' (Diana Reyes)."
        )

    # Check billing is contingency at ~35%
    billing = matter.get("billing", {})
    method = matter.get("billingMethod", billing.get("method"))
    if method != "contingency":
        errors.append(
            f"Billing method is '{method}', expected 'contingency'."
        )
    else:
        cont_fee = billing.get("contingencyFee", {})
        if cont_fee:
            pct = float(cont_fee.get("percentage", 0))
            if abs(pct - 35) > 3:
                errors.append(
                    f"Contingency percentage is {pct}%, expected ~35%."
                )
        else:
            errors.append("No contingency fee configured.")

    # Check settlement recovery ~$175,000
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 175000) < 15000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$175,000 found. Recovery amounts: {amounts}.")

    if errors:
        return False, "Mills v. Rodriguez changes not applied correctly. " + " | ".join(errors)

    return True, (
        f"Mills v. Rodriguez ({matter_id}) correctly updated: "
        f"attorney changed to Diana Reyes, contingency at 35%, "
        f"$175,000 recovery added to settlement."
    )
