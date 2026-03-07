import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Cruz matter
    cruz = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if ("Cruz" in desc and "Metro" in desc) or mid == "mat_008":
            cruz = matter
            break

    if not cruz:
        return False, "Could not find the Cruz v. Metro Transit matter in state."

    providers = cruz.get("medicalProviders", [])

    # Find provider with contactId con_021 (Dr. Amanda Reeves)
    reeves_provider = None
    for mp in providers:
        if mp.get("contactId") == "con_021":
            reeves_provider = mp
            break

    if not reeves_provider:
        return False, "No medical provider with contactId 'con_021' (Dr. Amanda Reeves) found on the Cruz case."

    errors = []

    # Check treatmentComplete == true
    if reeves_provider.get("treatmentComplete") is not True:
        errors.append(f"treatmentComplete is {reeves_provider.get('treatmentComplete')}, expected true")

    # Check recordStatus == "Requested"
    if reeves_provider.get("recordStatus") != "Requested":
        errors.append(f"recordStatus is '{reeves_provider.get('recordStatus')}', expected 'Requested'")

    if errors:
        return False, "; ".join(errors)

    return True, "Dr. Reeves added as provider on Cruz case with treatment complete and records Requested."
