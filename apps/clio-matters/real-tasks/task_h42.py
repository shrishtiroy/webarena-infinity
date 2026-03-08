import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Lakeside Insurance contact
    lakeside = None
    for c in state.get("contacts", []):
        if "Lakeside Insurance" in (c.get("lastName") or ""):
            lakeside = c
            break
    if not lakeside:
        return False, "Lakeside Insurance contact not found."

    # Find Rodriguez matter and its Lakeside recovery's legal fee
    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez matter not found."

    rod_rec = None
    for r in rodriguez.get("settlement", {}).get("recoveries", []):
        if r.get("sourceContactId") == lakeside["id"]:
            rod_rec = r
            break
    if not rod_rec:
        return False, "Lakeside recovery not found on Rodriguez case."

    rod_lf = None
    for lf in rodriguez.get("settlement", {}).get("legalFees", []):
        if lf.get("recoveryId") == rod_rec["id"]:
            rod_lf = lf
            break
    if not rod_lf:
        return False, "Legal fee for Lakeside recovery not found on Rodriguez case."

    expected_rate = rod_lf.get("rate")
    expected_recipient = rod_lf.get("recipientId")

    # Find Foster matter
    foster = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Foster" in desc and "Slip and Fall" in desc:
            foster = m
            break
    if not foster:
        return False, "Foster slip-and-fall matter not found."

    # Check Foster has Lakeside recovery for $75,000
    foster_rec = None
    for r in foster.get("settlement", {}).get("recoveries", []):
        if r.get("sourceContactId") == lakeside["id"]:
            foster_rec = r
            break
    if not foster_rec:
        return False, "No Lakeside Insurance recovery found on Foster case."

    if foster_rec.get("amount") != 75000:
        return False, f"Foster Lakeside recovery amount is {foster_rec.get('amount')}, expected 75000."

    # Check legal fee
    foster_lf = None
    for lf in foster.get("settlement", {}).get("legalFees", []):
        if lf.get("recoveryId") == foster_rec["id"]:
            foster_lf = lf
            break
    if not foster_lf:
        return False, "No legal fee found for Foster's Lakeside recovery."

    errors = []
    if foster_lf.get("recipientId") != expected_recipient:
        errors.append(
            f"Legal fee recipient is '{foster_lf.get('recipientId')}', "
            f"expected '{expected_recipient}'."
        )
    if foster_lf.get("rate") != expected_rate:
        errors.append(
            f"Legal fee rate is {foster_lf.get('rate')}, expected {expected_rate}."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Foster Lakeside recovery ($75,000) and legal fee added matching Rodriguez's rate and recipient."
