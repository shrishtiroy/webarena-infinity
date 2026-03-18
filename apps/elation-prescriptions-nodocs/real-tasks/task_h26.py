import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("settings", {})
    errors = []

    if settings.get("defaultPharmacy") != "pharm_012":
        errors.append(f"Expected defaultPharmacy 'pharm_012' (Safeway), got '{settings.get('defaultPharmacy')}'.")

    if settings.get("defaultRefills") != 5:
        errors.append(f"Expected defaultRefills 5, got {settings.get('defaultRefills')}.")

    if settings.get("signatureRequired") is not False:
        errors.append(f"Expected signatureRequired False, got {settings.get('signatureRequired')}.")

    favs = settings.get("favoritesDrugIds", [])
    if "drug_033" in favs:
        errors.append("Sertraline (drug_033) is still in the favorites list.")
    if "drug_018" in favs:
        errors.append("Levothyroxine (drug_018) is still in the favorites list.")

    if errors:
        return False, " ".join(errors)

    return True, "Settings updated and Sertraline/Levothyroxine removed from favorites."
