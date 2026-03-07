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
            damages = matter.get("damages", [])
            for dmg in damages:
                dmg_desc = dmg.get("description", "") or ""
                if dmg_desc == "Emergency Room Visit":
                    amount = dmg.get("amount", 0)
                    if amount == 18500:
                        return True, "Emergency Room Visit damage updated to $18,500 on Rodriguez."
                    else:
                        return False, f"Found Emergency Room Visit damage but amount is {amount}, expected 18500."
            return False, "No damage with description 'Emergency Room Visit' found in Rodriguez damages."

    return False, "Could not find the Rodriguez matter in state."
