import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Rodriguez matter
    rodriguez = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Rodriguez" in desc or mid == "mat_001":
            rodriguez = matter
            break

    if not rodriguez:
        return False, "Could not find the Rodriguez matter in state."

    providers = rodriguez.get("medicalProviders", [])
    errors = []

    # Check 1: NM Hospital (con_018) provider, record ER_Admission_Report.pdf, comment with expected text
    nm_provider = None
    for mp in providers:
        if mp.get("contactId") == "con_018":
            nm_provider = mp
            break

    if not nm_provider:
        errors.append("No medical provider for Northwestern Memorial Hospital (con_018) found")
    else:
        records = nm_provider.get("medicalRecords", [])
        er_record = None
        for rec in records:
            if rec.get("fileName") == "ER_Admission_Report.pdf":
                er_record = rec
                break

        if not er_record:
            errors.append("ER_Admission_Report.pdf not found in NM Hospital records")
        else:
            comments = er_record.get("comments", [])
            comment_texts = [c.get("text", "") for c in comments]
            target_text = "Critical documentation for settlement negotiations"
            found = any(target_text in t for t in comment_texts)
            if not found:
                errors.append(f"Comment '{target_text}' not found on ER_Admission_Report.pdf. Comments: {comment_texts}")

    # Check 2: Chicago PT (con_019) provider, bill CPTC_Bill_Full.pdf, comment with expected text
    cpt_provider = None
    for mp in providers:
        if mp.get("contactId") == "con_019":
            cpt_provider = mp
            break

    if not cpt_provider:
        errors.append("No medical provider for Chicago Physical Therapy Center (con_019) found")
    else:
        bills = cpt_provider.get("medicalBills", [])
        cptc_bill = None
        for bill in bills:
            if bill.get("fileName") == "CPTC_Bill_Full.pdf":
                cptc_bill = bill
                break

        if not cptc_bill:
            errors.append("CPTC_Bill_Full.pdf not found in Chicago PT bills")
        else:
            comments = cptc_bill.get("comments", [])
            comment_texts = [c.get("text", "") for c in comments]
            target_text = "Insurance payment verified"
            found = any(target_text in t for t in comment_texts)
            if not found:
                errors.append(f"Comment '{target_text}' not found on CPTC_Bill_Full.pdf. Comments: {comment_texts}")

    if errors:
        return False, "; ".join(errors)

    return True, "Comments added to ER_Admission_Report.pdf and CPTC_Bill_Full.pdf on Rodriguez case."
