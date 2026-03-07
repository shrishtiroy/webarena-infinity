import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    practice_areas = state.get("practiceAreas", [])
    found_insurance_law = False
    found_insurance_defense = False

    for pa in practice_areas:
        if pa.get("name") == "Insurance Law":
            found_insurance_law = True
        if pa.get("name") == "Insurance Defense":
            found_insurance_defense = True

    if found_insurance_defense:
        return False, "Practice area 'Insurance Defense' still exists; it should have been renamed."
    if not found_insurance_law:
        return False, "Practice area 'Insurance Law' not found in practiceAreas."

    return True, "Practice area renamed from 'Insurance Defense' to 'Insurance Law' successfully."
