import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    medical_providers = state.get("medicalProviders", [])
    for mp in medical_providers:
        if mp.get("matterId") == "matter_1" and mp.get("contactId") == "contact_56":
            return False, (
                "Medical provider with contactId 'contact_56' (Bay Area Orthopedic Associates) "
                "on matter_1 still exists but should have been deleted."
            )

    return True, "Medical provider with contactId 'contact_56' on matter_1 has been successfully deleted."
