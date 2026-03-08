import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    harris = next(
        (m for m in state.get("matters", [])
         if "Harris" in (m.get("description") or "") and "Workplace" in (m.get("description") or "")),
        None,
    )
    if not harris:
        return False, "Harris workplace injury matter not found."

    lakeside = next(
        (c for c in state.get("contacts", [])
         if "Lakeside" in (c.get("lastName") or "")),
        None,
    )
    espinoza = next(
        (c for c in state.get("contacts", [])
         if c.get("lastName") == "Espinoza"),
        None,
    )
    if not lakeside or not espinoza:
        return False, "Required contacts not found."

    resp_atty = harris.get("responsibleAttorneyId")

    errors = []

    # Check recovery
    recovery = next(
        (r for r in harris.get("settlement", {}).get("recoveries", [])
         if r.get("sourceContactId") == lakeside["id"] and r.get("amount") == 75000),
        None,
    )
    if not recovery:
        errors.append("No $75,000 recovery from Lakeside Insurance found.")
    else:
        # Check legal fee
        fee = next(
            (f for f in harris.get("settlement", {}).get("legalFees", [])
             if f.get("recoveryId") == recovery["id"]),
            None,
        )
        if not fee:
            errors.append("No legal fee found for the Lakeside recovery.")
        else:
            if fee.get("recipientId") != resp_atty:
                errors.append(
                    f"Legal fee recipient is '{fee.get('recipientId')}', "
                    f"expected '{resp_atty}' (Harris responsible attorney)."
                )
            if fee.get("rate") != 35:
                errors.append(f"Legal fee rate is {fee.get('rate')}%, expected 35%.")

            referrals = fee.get("referralFees", [])
            referral = next(
                (rf for rf in referrals if rf.get("recipientId") == espinoza["id"]),
                None,
            )
            if not referral:
                errors.append("No referral fee to Carlos Espinoza found.")
            elif referral.get("rate") != 5:
                errors.append(f"Referral fee rate is {referral.get('rate')}%, expected 5%.")

    if errors:
        return False, " ".join(errors)

    return True, "Harris: Lakeside recovery + legal fee at 35% + 5% referral to Espinoza."
