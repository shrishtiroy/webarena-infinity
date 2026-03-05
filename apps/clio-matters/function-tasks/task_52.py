import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    damages = state.get("damages", [])
    matching = [d for d in damages if d.get("matterId") == "matter_1" and d.get("name") == "Lumbar MRI and diagnostic imaging"]
    if not matching:
        return False, "Damage 'Lumbar MRI and diagnostic imaging' on matter_1 not found."

    damage = matching[0]
    damage_type = damage.get("type")
    if damage_type != "general":
        return False, f"Expected damage type 'general', got '{damage_type}'."

    return True, "Damage 'Lumbar MRI and diagnostic imaging' on matter_1 has type 'general'."
