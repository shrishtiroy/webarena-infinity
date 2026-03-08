import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contacts
    premier = None
    espinoza = None
    for c in state.get("contacts", []):
        name = c.get("lastName") or ""
        if "Premier Auto" in name:
            premier = c
        elif "Espinoza" in name:
            espinoza = c

    if not premier:
        return False, "Premier Auto Dealers contact not found."
    if not espinoza:
        return False, "Carlos Espinoza contact not found."

    # Find Rodriguez matter
    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez matter not found."

    # Find Premier Auto recovery
    premier_rec = None
    for r in rodriguez.get("settlement", {}).get("recoveries", []):
        if r.get("sourceContactId") == premier["id"]:
            premier_rec = r
            break
    if not premier_rec:
        return False, "Premier Auto Dealers recovery not found."

    # Find its legal fee
    lf = None
    for f in rodriguez.get("settlement", {}).get("legalFees", []):
        if f.get("recoveryId") == premier_rec["id"]:
            lf = f
            break
    if not lf:
        return False, "Legal fee for Premier Auto recovery not found."

    errors = []

    # Check discount is 10
    if lf.get("discount") != 10:
        errors.append(f"Discount is {lf.get('discount')}, expected 10.")

    # Check referral fee of 7.5% to Espinoza
    referrals = lf.get("referralFees", [])
    espinoza_referral = next(
        (rf for rf in referrals if rf.get("recipientId") == espinoza["id"]),
        None,
    )
    if not espinoza_referral:
        errors.append("No referral fee to Carlos Espinoza found.")
    elif espinoza_referral.get("rate") is None or abs(espinoza_referral["rate"] - 7.5) > 0.02:
        errors.append(
            f"Espinoza referral rate is {espinoza_referral.get('rate')}, expected 7.5."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Premier Auto legal fee: discount set to 10%, Espinoza referral at 7.5% added."
