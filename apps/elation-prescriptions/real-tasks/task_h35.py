import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify default pharmacy set to patient's secondary pharmacy (Walgreens #7892)."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    patient = state.get("currentPatient", {})
    errors = []

    secondary_pharm_id = patient.get("secondaryPharmacyId")
    default_pharm_id = settings.get("defaultPharmacyId")

    # Default pharmacy should match the patient's secondary pharmacy (pharm_003)
    if default_pharm_id != "pharm_003":
        errors.append(
            f"Default pharmacy is '{default_pharm_id}', expected 'pharm_003' (Walgreens #7892, "
            f"the patient's secondary pharmacy)"
        )

    if default_pharm_id == "pharm_001":
        errors.append("Default pharmacy is still the original CVS #4521, expected it to be changed")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Default pharmacy changed to patient's secondary pharmacy (Walgreens #7892) successfully."
    )
