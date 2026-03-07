import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Riverside Community Credit Union contact id
    contacts = state.get("contacts", [])
    riverside_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Riverside" in name and "Credit Union" in name:
            riverside_id = contact.get("id", "")
            break
    if not riverside_id:
        riverside_id = "con_028"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            settlement = matter.get("settlement", {})
            outstanding = settlement.get("outstandingBalances", [])
            # Look for a NEW entry (not ob_001) with balanceHolderId == riverside_id
            for ob in outstanding:
                ob_id = ob.get("id", "")
                if ob_id == "ob_001":
                    continue
                if ob.get("balanceHolderId") == riverside_id:
                    balance = ob.get("balanceOwing", 0)
                    party = ob.get("responsibleParty", "")
                    ob_desc = ob.get("description", "") or ""
                    errors = []
                    if balance != 2500:
                        errors.append(f"balanceOwing is {balance}, expected 2500")
                    if party != "other":
                        errors.append(f"responsibleParty is '{party}', expected 'other'")
                    if "Personal loan" not in ob_desc:
                        errors.append(f"description is '{ob_desc}', expected to contain 'Personal loan'")
                    if errors:
                        return False, f"Found new Riverside CU balance but: {'; '.join(errors)}."
                    return True, "New outstanding balance of $2,500 from Riverside CU added to Rodriguez settlement."
            return False, "No new outstanding balance from Riverside Community Credit Union found (besides existing ob_001)."

    return False, "Could not find the Rodriguez matter in state."
