import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        display_number = matter.get("displayNumber", "")
        if "Singh" in display_number:
            desc = matter.get("description", "")
            if desc == "Singh Family Revocable Living Trust":
                return True, f"Matter with displayNumber containing 'Singh' has description '{desc}' as expected."
            else:
                return False, f"Matter with displayNumber containing 'Singh' has description '{desc}', expected 'Singh Family Revocable Living Trust'."

    return False, "No matter found with displayNumber containing 'Singh'."
