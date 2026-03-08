import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the matter that was open with the highest trust fund balance (TechNova, $50k)
    # It should now be closed, and its responsible attorney assigned to Singh
    best_matter = None
    best_trust = -1
    all_matters = state.get("matters", [])

    # We need to identify the matter by description since it could be closed now
    # In seed data, TechNova has highest trust ($50,000)
    technova = None
    for m in all_matters:
        if "TechNova" in (m.get("description") or ""):
            technova = m
            break
    if not technova:
        return False, "TechNova matter not found."

    # Verify it's closed
    if technova.get("status") != "Closed":
        return False, (
            f"TechNova status is '{technova.get('status')}', expected 'Closed' "
            f"(it had the highest trust fund balance among open matters)."
        )

    # Find Singh matter and verify its responsible attorney matches TechNova's
    singh = None
    for m in all_matters:
        if "Singh" in (m.get("description") or ""):
            singh = m
            break
    if not singh:
        return False, "Singh estate matter not found."

    expected_atty = technova.get("responsibleAttorneyId")
    if singh.get("responsibleAttorneyId") != expected_atty:
        return False, (
            f"Singh responsible attorney is '{singh.get('responsibleAttorneyId')}', "
            f"expected '{expected_atty}' (TechNova's responsible attorney)."
        )

    return True, "TechNova closed and its responsible attorney assigned to Singh."
