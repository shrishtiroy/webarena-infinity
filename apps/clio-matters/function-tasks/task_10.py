import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find "Tax Law" practice area ID
    practice_areas = state.get("practiceAreas", [])
    tax_law_id = None
    for pa in practice_areas:
        if pa.get("name", "") == "Tax Law":
            tax_law_id = pa.get("id")
            break

    if tax_law_id is None:
        return False, "Could not find practice area named 'Tax Law'."

    # Find the matter
    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Singh Family" in desc:
            pa_id = matter.get("practiceAreaId", "")
            if pa_id == tax_law_id:
                return True, f"Matter '{desc}' has practiceAreaId '{tax_law_id}' (Tax Law) as expected."
            else:
                return False, f"Matter '{desc}' has practiceAreaId '{pa_id}', expected '{tax_law_id}' (Tax Law)."

    return False, "No matter found with description containing 'Singh Family'."
