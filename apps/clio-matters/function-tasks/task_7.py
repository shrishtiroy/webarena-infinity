import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find James Chen's user ID
    firm_users = state.get("firmUsers", [])
    james_chen_id = None
    for user in firm_users:
        if user.get("fullName", "") == "James Chen":
            james_chen_id = user.get("id")
            break

    if james_chen_id is None:
        return False, "Could not find firm user 'James Chen'."

    # Find the matter
    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Foster" in desc and "Evanston" in desc:
            responsible_attorney = matter.get("responsibleAttorneyId", "")
            if responsible_attorney == james_chen_id:
                return True, f"Matter '{desc}' has responsibleAttorneyId '{james_chen_id}' (James Chen) as expected."
            else:
                return False, f"Matter '{desc}' has responsibleAttorneyId '{responsible_attorney}', expected '{james_chen_id}' (James Chen)."

    return False, "No matter found with description containing 'Foster' and 'Evanston'."
