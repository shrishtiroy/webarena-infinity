import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    if not practice_areas:
        return False, "No practice areas found in state."

    corporate_found = False
    others_primary = []

    for pa in practice_areas:
        name = pa.get("name", "")
        is_primary = pa.get("isPrimary", False)
        if name == "Corporate Law":
            corporate_found = True
            if not is_primary:
                return False, "Corporate Law practice area exists but isPrimary is not true."
        else:
            if is_primary:
                others_primary.append(name)

    if not corporate_found:
        return False, "Corporate Law practice area not found."

    if others_primary:
        return False, f"Other practice areas still have isPrimary=true: {others_primary}"

    return True, "Corporate Law is set as the primary practice area and no others are primary."
