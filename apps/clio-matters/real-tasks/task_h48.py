import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contacts
    nm_hospital = None
    cptc = None
    garcia = None
    for c in state.get("contacts", []):
        name = c.get("lastName") or ""
        if "Northwestern Memorial" in name:
            nm_hospital = c
        elif "Chicago Physical Therapy" in name:
            cptc = c
    for u in state.get("firmUsers", []):
        if u.get("fullName") == "Maria Garcia":
            garcia = u

    if not nm_hospital:
        return False, "Northwestern Memorial Hospital contact not found."
    if not cptc:
        return False, "Chicago Physical Therapy Center contact not found."
    if not garcia:
        return False, "Maria Garcia user not found."

    # Find Cruz matter
    cruz = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Cruz" in desc and "Metro Transit" in desc:
            cruz = m
            break
    if not cruz:
        return False, "Cruz bus accident matter not found."

    settlement = cruz.get("settlement", {})
    errors = []

    # Check recovery from NM Hospital for $45,000
    nm_rec = None
    for r in settlement.get("recoveries", []):
        if r.get("sourceContactId") == nm_hospital["id"] and r.get("amount") == 45000:
            nm_rec = r
            break
    if not nm_rec:
        errors.append("No $45,000 recovery from Northwestern Memorial Hospital found.")

    # Check legal fee for that recovery
    if nm_rec:
        lf = None
        for f in settlement.get("legalFees", []):
            if f.get("recoveryId") == nm_rec["id"]:
                lf = f
                break
        if not lf:
            errors.append("No legal fee found for NM Hospital recovery.")
        else:
            if lf.get("recipientId") != garcia["id"]:
                errors.append(
                    f"Legal fee recipient is '{lf.get('recipientId')}', "
                    f"expected '{garcia['id']}'."
                )
            if lf.get("rate") is None or abs(lf["rate"] - 33.33) > 0.02:
                errors.append(f"Legal fee rate is {lf.get('rate')}, expected 33.33.")
            if lf.get("discount") != 5:
                errors.append(f"Legal fee discount is {lf.get('discount')}, expected 5.")

    # Check lien from CPTC for $3,500
    cptc_lien = None
    for ln in settlement.get("otherLiens", []):
        if ln.get("lienHolderId") == cptc["id"]:
            cptc_lien = ln
            break
    if not cptc_lien:
        errors.append("No lien from Chicago Physical Therapy Center found.")
    else:
        if cptc_lien.get("amount") != 3500:
            errors.append(
                f"CPTC lien amount is {cptc_lien.get('amount')}, expected 3500."
            )
        if cptc_lien.get("description") != "Outstanding treatment balance":
            errors.append(
                f"CPTC lien description is '{cptc_lien.get('description')}', "
                f"expected 'Outstanding treatment balance'."
            )

    if errors:
        return False, " ".join(errors)

    return True, "Cruz settlement: NM Hospital recovery, legal fee, and CPTC lien all added correctly."
