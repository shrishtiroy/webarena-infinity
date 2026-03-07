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
                if "ental" in dmg_desc:
                    amount = dmg.get("amount", 0)
                    category = dmg.get("category", "")
                    dmg_type = dmg.get("type", "")
                    errors = []
                    if amount != 4200:
                        errors.append(f"amount is {amount}, expected 4200")
                    if category != "Special":
                        errors.append(f"category is '{category}', expected 'Special'")
                    if dmg_type != "Property Damage":
                        errors.append(f"type is '{dmg_type}', expected 'Property Damage'")
                    if errors:
                        return False, f"Found rental car damage entry but: {'; '.join(errors)}."
                    return True, "Rental car expense of $4,200 added as Property Damage to Rodriguez case."
            return False, "No damage entry containing 'ental' (rental) found in Rodriguez damages."

    return False, "Could not find the Rodriguez matter in state."
