import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        matter_id = matter.get("id", "")
        if "Mendez" in desc or matter_id == "mat_011":
            location = matter.get("location", "")
            if location == "Chicago":
                return True, "Mendez work visa matter location is now Chicago."
            else:
                return False, f"Mendez work visa matter location is '{location}', expected 'Chicago'."

    return False, "Could not find the Mendez work visa matter in state."
