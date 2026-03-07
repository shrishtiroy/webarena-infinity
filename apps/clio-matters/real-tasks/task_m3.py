import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Northwestern Memorial Hospital contact id
    contacts = state.get("contacts", [])
    nm_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Northwestern Memorial" in name:
            nm_id = contact.get("id", "")
            break
    if not nm_id:
        nm_id = "con_018"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            settlement = matter.get("settlement", {})
            other_liens = settlement.get("otherLiens", [])
            for lien in other_liens:
                if lien.get("lienHolderId") == nm_id:
                    amount = lien.get("amount", 0)
                    lien_desc = lien.get("description", "") or ""
                    errors = []
                    if amount != 12000:
                        errors.append(f"amount is {amount}, expected 12000")
                    if "Hospital treatment balance" not in lien_desc:
                        errors.append(f"description is '{lien_desc}', expected to contain 'Hospital treatment balance'")
                    if errors:
                        return False, f"Found NM Hospital lien but: {'; '.join(errors)}."
                    return True, "Lien of $12,000 from Northwestern Memorial Hospital added to Rodriguez settlement."
            return False, "No lien from Northwestern Memorial Hospital found in Rodriguez settlement."

    return False, "Could not find the Rodriguez matter in state."
