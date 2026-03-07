import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Rodriguez v. Premier Auto matter
    matters = state.get("matters", [])
    rodriguez_matter = None
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez v. Premier Auto" in desc or matter_id == "mat_001":
            rodriguez_matter = matter
            break

    if not rodriguez_matter:
        return False, "Could not find the Rodriguez v. Premier Auto matter in state."

    # Find medical provider with contactId con_021 (Dr. Amanda Reeves)
    medical_providers = rodriguez_matter.get("medicalProviders", [])
    if not medical_providers:
        return False, "No medical providers found on the Rodriguez matter."

    for mp in medical_providers:
        contact_id = mp.get("contactId", "")
        mp_name = mp.get("name", "") or mp.get("providerName", "") or ""
        if contact_id == "con_021" or "Amanda Reeves" in mp_name:
            treatment_complete = mp.get("treatmentComplete", False)
            if treatment_complete is True:
                return True, "Dr. Amanda Reeves treatment is marked as complete on the Rodriguez case."
            else:
                return False, f"Dr. Amanda Reeves treatmentComplete is {treatment_complete}, expected true."

    return False, "Could not find Dr. Amanda Reeves (con_021) among Rodriguez matter medical providers."
