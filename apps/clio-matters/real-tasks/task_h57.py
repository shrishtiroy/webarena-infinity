import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Dr. Amanda Reeves contact
    reeves = None
    for c in state.get("contacts", []):
        full = f"{c.get('firstName', '')} {c.get('lastName', '')}".strip()
        if "Reeves" in full and "Amanda" in full:
            reeves = c
            break
    if not reeves:
        return False, "Dr. Amanda Reeves contact not found."

    # Find Harris matter
    harris = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Harris" in desc and "Workplace" in desc:
            harris = m
            break
    if not harris:
        return False, "Harris workplace injury matter not found."

    # Find the Reeves provider on Harris
    provider = None
    for p in harris.get("medicalProviders", []):
        if p.get("contactId") == reeves["id"]:
            provider = p
            break
    if not provider:
        return False, "Dr. Amanda Reeves not found as medical provider on Harris case."

    errors = []

    if provider.get("description") != "Hand specialist evaluation":
        errors.append(
            f"Provider description is '{provider.get('description')}', "
            f"expected 'Hand specialist evaluation'."
        )
    if provider.get("treatmentFirstDate") != "2026-02-01":
        errors.append(
            f"Treatment first date is '{provider.get('treatmentFirstDate')}', "
            f"expected '2026-02-01'."
        )
    if provider.get("treatmentComplete") is not True:
        errors.append("Treatment should be marked complete.")

    # Check medical record
    records = provider.get("medicalRecords", [])
    record = next(
        (r for r in records if r.get("fileName") == "Hand_Specialist_Report.pdf"),
        None,
    )
    if not record:
        errors.append("Medical record 'Hand_Specialist_Report.pdf' not found.")
    elif record.get("receivedDate") != "2026-03-05":
        errors.append(
            f"Record received date is '{record.get('receivedDate')}', "
            f"expected '2026-03-05'."
        )

    # Check medical bill
    bills = provider.get("medicalBills", [])
    bill = next(
        (b for b in bills if b.get("fileName") == "Reeves_Consult_Bill.pdf"),
        None,
    )
    if not bill:
        errors.append("Medical bill 'Reeves_Consult_Bill.pdf' not found.")
    else:
        if bill.get("billAmount") != 4500:
            errors.append(
                f"Bill amount is {bill.get('billAmount')}, expected 4500."
            )
        if bill.get("adjustment") != 500:
            errors.append(
                f"Bill adjustment is {bill.get('adjustment')}, expected 500."
            )

    if errors:
        return False, " ".join(errors)

    return True, "Dr. Reeves added to Harris with record, bill, and treatment details."
