import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Nguyen" in desc and "Divorce" in desc:
            status = matter.get("status", "")
            if status == "Closed":
                return True, f"Matter '{desc}' has status 'Closed' as expected."
            else:
                return False, f"Matter '{desc}' has status '{status}', expected 'Closed'."

    return False, "No matter found with description containing 'Nguyen' and 'Divorce'."
