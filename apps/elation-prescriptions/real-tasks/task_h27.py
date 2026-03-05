import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Codeine and Latex allergies removed, Tramadol allergy added."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    allergies = state.get("currentPatient", {}).get("allergies", [])
    errors = []

    # --- Codeine should NOT be in allergies ---
    for allergy in allergies:
        if (allergy.get("allergen") or "").lower() == "codeine":
            errors.append("Codeine allergy still present in patient's allergies")
            break

    # --- Latex should NOT be in allergies ---
    for allergy in allergies:
        if (allergy.get("allergen") or "").lower() == "latex":
            errors.append("Latex allergy still present in patient's allergies")
            break

    # --- Tramadol should be in allergies ---
    tramadol_allergy = None
    for allergy in allergies:
        if "tramadol" in (allergy.get("allergen") or "").lower():
            tramadol_allergy = allergy
            break

    if tramadol_allergy is None:
        allergen_names = [a.get("allergen", "") for a in allergies]
        errors.append(
            f"Tramadol allergy not found. Current allergens: {allergen_names}"
        )
    else:
        # Check severity is Moderate
        severity = (tramadol_allergy.get("severity") or "").lower()
        if severity != "moderate":
            errors.append(
                f"Tramadol allergy severity is '{tramadol_allergy.get('severity')}', expected 'Moderate'"
            )

        # Check type is drug
        allergy_type = (tramadol_allergy.get("type") or "").lower()
        if allergy_type != "drug":
            errors.append(
                f"Tramadol allergy type is '{tramadol_allergy.get('type')}', expected 'drug'"
            )

    # Penicillin and Sulfonamides should still be there
    remaining = {(a.get("allergen") or "").lower() for a in allergies}
    if "penicillin" not in remaining:
        errors.append("Penicillin allergy was accidentally removed")
    if "sulfonamides" not in remaining:
        errors.append("Sulfonamides allergy was accidentally removed")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Codeine and Latex allergies removed, Tramadol allergy added "
        f"(severity: {tramadol_allergy.get('severity')}, type: {tramadol_allergy.get('type')})."
    )
