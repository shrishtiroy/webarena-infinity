import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find David Kim's user ID
    firm_users = state.get("firmUsers", [])
    david_kim_id = None
    for user in firm_users:
        if user.get("fullName", "") == "David Kim":
            david_kim_id = user.get("id")
            break

    if david_kim_id is None:
        return False, "Could not find firm user 'David Kim'."

    # Find the matter
    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Mendez" in desc and "Work Visa" in desc:
            originating_attorney = matter.get("originatingAttorneyId", "")
            if originating_attorney == david_kim_id:
                return True, f"Matter '{desc}' has originatingAttorneyId '{david_kim_id}' (David Kim) as expected."
            else:
                return False, f"Matter '{desc}' has originatingAttorneyId '{originating_attorney}', expected '{david_kim_id}' (David Kim)."

    return False, "No matter found with description containing 'Mendez' and 'Work Visa'."
