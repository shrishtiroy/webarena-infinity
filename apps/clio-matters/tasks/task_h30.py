import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the McCarthy pedestrian matter
    matter = next(
        (m for m in state.get("matters", [])
         if "mccarthy" in m.get("description", "").lower()
         and "pedestrian" in m.get("description", "").lower()),
        None
    )
    if matter is None:
        return False, "Could not find McCarthy pedestrian matter."

    matter_id = matter["id"]

    # Find the chiropractic provider for this matter
    # mp_12: Dr. Michael Reeves Chiropractic (contact_60)
    providers = [
        mp for mp in state.get("medicalProviders", [])
        if mp.get("matterId") == matter_id
    ]

    chiro_provider = next(
        (mp for mp in providers
         if mp.get("contactId") == "contact_60"
         or "chiropractic" in mp.get("description", "").lower()
         or "chiropract" in mp.get("description", "").lower()),
        None
    )

    if chiro_provider is None:
        provider_descs = [(mp.get("id"), mp.get("description")) for mp in providers]
        return False, (
            f"No chiropractic provider found for McCarthy pedestrian matter ({matter_id}). "
            f"Providers: {provider_descs}."
        )

    # Check record status
    if chiro_provider.get("recordStatus") != "received":
        errors.append(
            f"Chiropractic provider record status is '{chiro_provider.get('recordStatus')}', "
            f"expected 'received'."
        )

    # Check bill status
    if chiro_provider.get("billStatus") != "received":
        errors.append(
            f"Chiropractic provider bill status is '{chiro_provider.get('billStatus')}', "
            f"expected 'received'."
        )

    # Check first treatment date
    first_treatment = chiro_provider.get("firstTreatmentDate")
    if first_treatment != "2024-10-15":
        errors.append(
            f"Chiropractic provider first treatment date is '{first_treatment}', "
            f"expected '2024-10-15'."
        )

    if errors:
        return False, (
            f"McCarthy chiropractic provider ({chiro_provider.get('id')}) not updated correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"McCarthy chiropractic provider ({chiro_provider.get('id')}) updated: "
        f"record status=received, bill status=received, first treatment=2024-10-15."
    )
