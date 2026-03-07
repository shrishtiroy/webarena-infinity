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
            other_liens = settlement.get("otherLiens", [])
            for lien in other_liens:
                if lien.get("lienHolderId") == riverside_id:
                    reduction = lien.get("reduction", 0)
                    if reduction == 1000:
                        return True, "Riverside CU lien reduction set to $1,000 on Rodriguez settlement."
                    else:
                        return False, f"Found Riverside CU lien but reduction is {reduction}, expected 1000."
            return False, "No lien from Riverside Community Credit Union found in Rodriguez settlement."

    return False, "Could not find the Rodriguez matter in state."
