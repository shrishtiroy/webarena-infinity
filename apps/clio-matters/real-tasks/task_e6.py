import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    if not practice_areas:
        return False, "No practice areas found in state."

    found_insurance_law = False
    found_insurance_defense = False

    for pa in practice_areas:
        name = pa.get("name", "")
        if name == "Insurance Law":
            found_insurance_law = True
        if name == "Insurance Defense":
            found_insurance_defense = True

    if found_insurance_defense:
        return False, "Insurance Defense practice area still exists."

    if not found_insurance_law:
        return False, "Insurance Law practice area not found."

    return True, "Insurance Defense has been renamed to Insurance Law."
