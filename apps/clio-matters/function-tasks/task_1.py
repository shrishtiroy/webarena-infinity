import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Rodriguez v. Premier Auto" in desc:
            status = matter.get("status", "")
            if status == "Pending":
                return True, f"Matter '{desc}' has status 'Pending' as expected."
            else:
                return False, f"Matter '{desc}' has status '{status}', expected 'Pending'."

    return False, "No matter found with description containing 'Rodriguez v. Premier Auto'."
