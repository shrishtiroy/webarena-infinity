import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Melatonin (sleep OTC) was discontinued."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_otc_meds = state.get("permanentOtcMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    errors = []

    # Melatonin should NOT be in permanentOtcMeds
    for med in permanent_otc_meds:
        if "Melatonin" in (med.get("medicationName") or ""):
            errors.append(
                f"Melatonin still in permanentOtcMeds: '{med.get('medicationName')}'"
            )
            break

    # Melatonin should be in discontinuedMeds
    melatonin_disc = None
    for med in discontinued_meds:
        if "Melatonin" in (med.get("medicationName") or ""):
            melatonin_disc = med
            break

    if melatonin_disc is None:
        errors.append("Melatonin not found in discontinuedMeds")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Melatonin (bedtime sleep supplement) discontinued successfully."
    )
