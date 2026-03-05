import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Ciprofloxacin discontinued and default pharmacy changed to Rite Aid #3456."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    temporary_meds = state.get("temporaryMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    settings = state.get("settings", {})
    errors = []

    # --- Part A: Ciprofloxacin should NOT be in temporaryMeds ---
    for med in temporary_meds:
        if "Ciprofloxacin" in (med.get("medicationName") or ""):
            errors.append(f"Ciprofloxacin still in temporaryMeds: '{med.get('medicationName')}'")
            break

    # Ciprofloxacin should be in discontinuedMeds
    cipro_disc = None
    for med in discontinued_meds:
        if "Ciprofloxacin" in (med.get("medicationName") or ""):
            cipro_disc = med
            break

    if cipro_disc is None:
        errors.append("Ciprofloxacin not found in discontinuedMeds")

    # --- Part B: Default pharmacy should be Rite Aid #3456 (pharm_005) ---
    default_pharm = settings.get("defaultPharmacyId")
    if default_pharm != "pharm_005":
        errors.append(
            f"Default pharmacy is '{default_pharm}', expected 'pharm_005' (Rite Aid #3456)"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Ciprofloxacin discontinued and default pharmacy changed to Rite Aid #3456 successfully."
    )
