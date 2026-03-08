import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Okafor DUI matter to get client
    okafor = next(
        (m for m in state.get("matters", [])
         if "Okafor" in (m.get("description") or "") and "DUI" in (m.get("description") or "")),
        None,
    )
    if not okafor:
        return False, "Okafor DUI matter not found."
    expected_client = okafor.get("clientId")

    # Find Criminal Law practice area
    criminal = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("name") == "Criminal Law"),
        None,
    )
    if not criminal:
        return False, "Criminal Law practice area not found."

    # Find Michael Osei
    osei = next(
        (u for u in state.get("firmUsers", [])
         if u.get("fullName") == "Michael Osei"),
        None,
    )
    if not osei:
        return False, "Michael Osei not found."

    # Find the new matter
    new_matter = next(
        (m for m in state.get("matters", [])
         if "Okafor" in (m.get("description") or "")
         and "Civil Rights" in (m.get("description") or "")),
        None,
    )
    if not new_matter:
        return False, "New matter 'Okafor - Civil Rights Claim' not found."

    errors = []
    if new_matter.get("clientId") != expected_client:
        errors.append(
            f"Client is '{new_matter.get('clientId')}', expected '{expected_client}'."
        )
    if new_matter.get("practiceAreaId") != criminal["id"]:
        errors.append(
            f"Practice area is '{new_matter.get('practiceAreaId')}', "
            f"expected '{criminal['id']}'."
        )
    if new_matter.get("responsibleAttorneyId") != osei["id"]:
        errors.append(
            f"Responsible attorney is '{new_matter.get('responsibleAttorneyId')}', "
            f"expected '{osei['id']}'."
        )
    billing = new_matter.get("billingPreference", {}).get("billingMethod")
    if billing != "hourly":
        errors.append(f"Billing method is '{billing}', expected 'hourly'.")

    if errors:
        return False, " ".join(errors)

    return True, "New matter created for Okafor client under Criminal Law with Osei and hourly billing."
