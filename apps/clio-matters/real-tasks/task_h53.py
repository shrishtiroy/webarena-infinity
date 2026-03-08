import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez matter not found."

    damages = rodriguez.get("damages", [])
    errors = []

    # Seed Special damages under $20,000 that should be deleted:
    # ER Visit ($15,800), PT 24 sessions ($12,000), Vehicle repair ($18,200)
    should_be_gone = ["Emergency Room Visit", "Physical Therapy (24 sessions)", "Vehicle repair costs"]
    for desc_text in should_be_gone:
        found = any(d.get("description") == desc_text for d in damages)
        if found:
            errors.append(f"Damage '{desc_text}' should have been deleted (Special, under $20k).")

    # Orthopedic Surgery should be $90,000
    ortho = [d for d in damages if d.get("description") == "Orthopedic Surgery"]
    if not ortho:
        errors.append("'Orthopedic Surgery' damage not found.")
    elif ortho[0].get("amount") != 90000:
        errors.append(
            f"Orthopedic Surgery amount is {ortho[0].get('amount')}, expected 90000."
        )

    # Special damages >= $20k should still exist
    should_remain = ["Lost wages - 14 weeks", "Future medical care estimate"]
    for desc_text in should_remain:
        found = any(d.get("description") == desc_text for d in damages)
        if not found:
            errors.append(f"Damage '{desc_text}' should still exist (Special, >= $20k).")

    # General damages should be untouched
    general_count = sum(1 for d in damages if d.get("category") == "General")
    if general_count != 3:
        errors.append(f"Expected 3 General damages (untouched), found {general_count}.")

    if errors:
        return False, " ".join(errors)

    return True, "Special damages under $20k deleted and Orthopedic Surgery updated to $90,000."
