import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00007":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00007'."

    expected_desc = "Okafor v. HomeComfort Appliances - Defective space heater causing severe burns and smoke inhalation"
    actual_desc = matter.get("description", "")

    if actual_desc != expected_desc:
        return False, f"Expected matter '00007-Okafor' description to be '{expected_desc}', but got '{actual_desc}'."

    return True, "Matter '00007-Okafor' description has been correctly updated."
