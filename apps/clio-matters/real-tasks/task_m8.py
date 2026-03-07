import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            client_ref = matter.get("clientRefNumber", "")
            location = matter.get("location", "")
            errors = []
            if client_ref != "REF-2026-UPDATED":
                errors.append(f"clientRefNumber is '{client_ref}', expected 'REF-2026-UPDATED'")
            if location != "Northern District of Illinois":
                errors.append(f"location is '{location}', expected 'Northern District of Illinois'")
            if errors:
                return False, f"Rodriguez matter found but: {'; '.join(errors)}."
            return True, "Rodriguez matter updated with clientRefNumber 'REF-2026-UPDATED' and location 'Northern District of Illinois'."

    return False, "Could not find the Rodriguez matter in state."
