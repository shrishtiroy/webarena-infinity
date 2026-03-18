import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("settings", {})
    errors = []

    favs = settings.get("favoritesDrugIds", [])

    # NSAID (Ibuprofen, drug_043) and corticosteroid (Prednisone, drug_045) should be removed
    if "drug_043" in favs:
        errors.append("Ibuprofen (drug_043, NSAID) is still in favorites.")
    if "drug_045" in favs:
        errors.append("Prednisone (drug_045, corticosteroid) is still in favorites.")

    # Clopidogrel (drug_048) and Rosuvastatin (drug_003) should be added
    if "drug_048" not in favs:
        errors.append("Clopidogrel (drug_048) was not added to favorites.")
    if "drug_003" not in favs:
        errors.append("Rosuvastatin (drug_003) was not added to favorites.")

    # Print format should be compact
    if settings.get("printFormat") != "compact":
        errors.append(f"Expected printFormat 'compact', got '{settings.get('printFormat')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "NSAID and corticosteroid removed, Clopidogrel and Rosuvastatin added, print format set to compact."
