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

    # Find Dr. Reeves provider (con_021)
    reeves_provider = None
    for mp in providers:
        if mp.get("contactId") == "con_021":
            reeves_provider = mp
            break

    if not reeves_provider:
        return False, "No medical provider for Dr. Amanda Reeves (con_021) found on Rodriguez case."

    errors = []

    # Check billStatus == "Requested"
    if reeves_provider.get("billStatus") != "Requested":
        errors.append(f"billStatus is '{reeves_provider.get('billStatus')}', expected 'Requested'")

    # Check billRequestDate contains "2026-03-01"
    bill_date = reeves_provider.get("billRequestDate", "") or ""
    if "2026-03-01" not in bill_date:
        errors.append(f"billRequestDate is '{bill_date}', expected to contain '2026-03-01'")

    # Check recordStatus == "Received"
    if reeves_provider.get("recordStatus") != "Received":
        errors.append(f"recordStatus is '{reeves_provider.get('recordStatus')}', expected 'Received'")

    if errors:
        return False, "; ".join(errors)

    return True, "Dr. Reeves provider on Rodriguez: bill Requested on 2026-03-01, records Received."
