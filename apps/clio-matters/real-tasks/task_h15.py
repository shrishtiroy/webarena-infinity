import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Rodriguez matter
    rodriguez = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Rodriguez" in desc or mid == "mat_001":
            rodriguez = matter
            break

    if not rodriguez:
        return False, "Could not find the Rodriguez matter in state."

    damages = rodriguez.get("damages", [])

    errors = []

    # Check 1: No damage with description == "Vehicle repair costs"
    for dmg in damages:
        if dmg.get("description") == "Vehicle repair costs":
            errors.append("Damage 'Vehicle repair costs' still exists; should have been deleted")
            break

    # Check 2: Damage with description containing "ental vehicle" or "Rental vehicle",
    # type "Out-of-Pocket Expenses", category "Special", amount 5500
    rental_found = False
    rental_errors = []
    for dmg in damages:
        ddesc = dmg.get("description", "") or ""
        if "ental vehicle" in ddesc or "ental Vehicle" in ddesc:
            rental_found = True
            if dmg.get("category") != "Special":
                rental_errors.append(f"Rental vehicle damage category is '{dmg.get('category')}', expected 'Special'")
            if dmg.get("type") != "Out-of-Pocket Expenses":
                rental_errors.append(f"Rental vehicle damage type is '{dmg.get('type')}', expected 'Out-of-Pocket Expenses'")
            if dmg.get("amount") != 5500:
                rental_errors.append(f"Rental vehicle damage amount is {dmg.get('amount')}, expected 5500")
            break

    if not rental_found:
        errors.append("No damage entry containing 'ental vehicle' (rental vehicle) found in Rodriguez damages")
    else:
        errors.extend(rental_errors)

    if errors:
        return False, "; ".join(errors)

    return True, "Vehicle repair costs deleted and rental vehicle/transportation $5,500 added to Rodriguez."
