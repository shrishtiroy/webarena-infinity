import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    medical_providers = state.get("medicalProviders", [])
    matches = [
        mp for mp in medical_providers
        if mp.get("matterId") == "matter_1" and mp.get("contactId") == "contact_60"
    ]

    if not matches:
        return False, "Medical provider with contactId 'contact_60' (Dr. Michael Reeves Chiropractic) on matter_1 not found."

    target = matches[0]
    description = (target.get("description") or "").lower()
    if "chiropractic" not in description and "cervical" not in description:
        return False, (
            f"Medical provider description '{target.get('description')}' does not contain "
            "'chiropractic' or 'cervical'."
        )

    return True, "Medical provider 'Dr. Michael Reeves Chiropractic' correctly added to matter_1."
