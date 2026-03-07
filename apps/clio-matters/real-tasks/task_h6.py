import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Harris matter
    harris = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if ("Harris" in desc and "ABC" in desc) or mid == "mat_013":
            harris = matter
            break

    if not harris:
        return False, "Could not find the Harris v. ABC Construction matter in state."

    damages = harris.get("damages", [])

    # Check 1: PT damage - description containing "physical therapy" (case insensitive), category Special, type Medical Expenses, amount 6000
    pt_found = False
    pt_errors = []
    for dmg in damages:
        ddesc = (dmg.get("description", "") or "").lower()
        if "physical therapy" in ddesc or "pt" in ddesc.split():
            pt_found = True
            if dmg.get("category") != "Special":
                pt_errors.append(f"PT damage category is '{dmg.get('category')}', expected 'Special'")
            if dmg.get("type") != "Medical Expenses":
                pt_errors.append(f"PT damage type is '{dmg.get('type')}', expected 'Medical Expenses'")
            if dmg.get("amount") != 6000:
                pt_errors.append(f"PT damage amount is {dmg.get('amount')}, expected 6000")
            break

    # Check 2: Emotional distress damage - description containing "emotional distress" (case insensitive), category General, type Emotional Distress, amount 25000
    ed_found = False
    ed_errors = []
    for dmg in damages:
        ddesc = (dmg.get("description", "") or "").lower()
        if "emotional distress" in ddesc:
            ed_found = True
            if dmg.get("category") != "General":
                ed_errors.append(f"Emotional distress damage category is '{dmg.get('category')}', expected 'General'")
            if dmg.get("type") != "Emotional Distress":
                ed_errors.append(f"Emotional distress damage type is '{dmg.get('type')}', expected 'Emotional Distress'")
            if dmg.get("amount") != 25000:
                ed_errors.append(f"Emotional distress damage amount is {dmg.get('amount')}, expected 25000")
            break

    errors = []
    if not pt_found:
        errors.append("No damage entry containing 'physical therapy' found in Harris damages")
    else:
        errors.extend(pt_errors)

    if not ed_found:
        errors.append("No damage entry containing 'emotional distress' found in Harris damages")
    else:
        errors.extend(ed_errors)

    if errors:
        return False, "; ".join(errors)

    return True, "Two new damages added to Harris case: Physical therapy $6,000 and Emotional distress $25,000."
