import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    technova = next(
        (m for m in state.get("matters", [])
         if "TechNova" in (m.get("description") or "")),
        None,
    )
    if not technova:
        return False, "TechNova matter not found."

    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    singh = next(
        (m for m in state.get("matters", [])
         if "Singh" in (m.get("description") or "")),
        None,
    )
    if not singh:
        return False, "Singh estate matter not found."

    errors = []
    expected_resp = technova.get("responsibleAttorneyId")
    expected_orig = rodriguez.get("originatingAttorneyId")

    if singh.get("responsibleAttorneyId") != expected_resp:
        errors.append(
            f"Responsible attorney is '{singh.get('responsibleAttorneyId')}', "
            f"expected '{expected_resp}' (TechNova's responsible attorney)."
        )
    if singh.get("originatingAttorneyId") != expected_orig:
        errors.append(
            f"Originating attorney is '{singh.get('originatingAttorneyId')}', "
            f"expected '{expected_orig}' (Rodriguez's originating attorney)."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Singh: responsible=TechNova's attorney, originating=Rodriguez's attorney."
