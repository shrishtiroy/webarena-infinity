import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find James Chen's user ID
    users = state.get("firmUsers", [])
    james_chen_id = None
    for user in users:
        full_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        name = user.get("name", "")
        if full_name == "James Chen" or name == "James Chen" or user.get("id") == "usr_002":
            james_chen_id = user.get("id", "usr_002")
            break

    if not james_chen_id:
        # Fall back to known ID
        james_chen_id = "usr_002"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if ("Harris" in desc and "ABC Construction" in desc) or matter_id == "mat_013":
            responsible = matter.get("responsibleAttorneyId", "")
            if responsible == james_chen_id:
                return True, f"Harris v. ABC Construction responsible attorney is now James Chen ({james_chen_id})."
            else:
                return False, f"Harris v. ABC Construction responsibleAttorneyId is '{responsible}', expected '{james_chen_id}'."

    return False, "Could not find the Harris v. ABC Construction matter in state."
