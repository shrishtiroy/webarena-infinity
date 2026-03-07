import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Rachel Thompson's user ID
    firm_users = state.get("firmUsers", [])
    rachel_id = None
    for user in firm_users:
        if user.get("fullName", "") == "Rachel Thompson":
            rachel_id = user.get("id")
            break

    if rachel_id is None:
        return False, "Could not find firm user 'Rachel Thompson'."

    # Find the matter
    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Harris" in desc and "ABC Construction" in desc:
            responsible_staff = matter.get("responsibleStaffId", "")
            if responsible_staff == rachel_id:
                return True, f"Matter '{desc}' has responsibleStaffId '{rachel_id}' (Rachel Thompson) as expected."
            else:
                return False, f"Matter '{desc}' has responsibleStaffId '{responsible_staff}', expected '{rachel_id}' (Rachel Thompson)."

    return False, "No matter found with description containing 'Harris' and 'ABC Construction'."
