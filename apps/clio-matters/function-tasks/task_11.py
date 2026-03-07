import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Mendez" in desc and "Work Visa" in desc:
            location = matter.get("location", "")
            if location == "Chicago":
                return True, f"Matter '{desc}' has location 'Chicago' as expected."
            else:
                return False, f"Matter '{desc}' has location '{location}', expected 'Chicago'."

    return False, "No matter found with description containing 'Mendez' and 'Work Visa'."
