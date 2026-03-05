import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Johnson v. Whole Foods matter
    matter = next(
        (m for m in state.get("matters", [])
         if "johnson" in m.get("description", "").lower()
         and "whole foods" in m.get("description", "").lower()),
        None,
    )
    if matter is None:
        return False, "Johnson v. Whole Foods case not found."

    matter_id = matter["id"]

    # Find UCSF Medical Center provider for this matter
    ucsf_provider = next(
        (p for p in state.get("medicalProviders", [])
         if p.get("matterId") == matter_id
         and (p.get("contactId") == "contact_59"
              or "ucsf" in p.get("description", "").lower())),
        None,
    )
    if ucsf_provider is None:
        return False, "UCSF Medical Center provider not found on Johnson v. Whole Foods case."

    provider_id = ucsf_provider["id"]

    # Check for new medical record (follow-up MRI, 2025-03-15, received)
    records = [
        r for r in state.get("medicalRecords", [])
        if r.get("providerId") == provider_id and r.get("matterId") == matter_id
    ]
    has_record = any(
        ("mri" in r.get("description", "").lower()
         or "follow" in r.get("description", "").lower())
        and r.get("status") == "received"
        for r in records
    )
    if not has_record:
        rec_list = [(r.get("description"), r.get("status"), r.get("date")) for r in records]
        errors.append(
            f"No follow-up MRI record with status 'received' found for UCSF provider. "
            f"Records: {rec_list}."
        )

    # Check for new medical bill (2025-03-15, $3,500, outstanding)
    bills = [
        b for b in state.get("medicalBills", [])
        if b.get("providerId") == provider_id and b.get("matterId") == matter_id
    ]
    has_bill = any(
        abs(float(b.get("billAmount", 0)) - 3500) < 500
        and b.get("status") == "outstanding"
        for b in bills
    )
    if not has_bill:
        bill_list = [(b.get("billAmount"), b.get("status"), b.get("billDate")) for b in bills]
        errors.append(
            f"No $3,500 outstanding bill found for UCSF provider. Bills: {bill_list}."
        )

    if errors:
        return False, (
            "UCSF provider records/bills not added correctly on Johnson case. "
            + " | ".join(errors)
        )

    return True, (
        "Follow-up MRI record (received) and $3,500 outstanding bill correctly added "
        "to UCSF Medical Center provider on Johnson v. Whole Foods case."
    )
