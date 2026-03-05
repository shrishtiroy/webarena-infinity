import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify alert settings tightened and inhalation sigs deleted."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    dds = settings.get("drugDecisionSupport", {})
    custom_sigs = state.get("customSigs", [])
    errors = []

    # --- Drug-to-drug level should be major_only ---
    level = dds.get("drugToDrugLevel")
    if level != "major_only":
        errors.append(
            f"drugToDrugLevel is '{level}', expected 'major_only'"
        )

    # --- Drug-to-allergy should be disabled ---
    allergy_enabled = dds.get("drugToAllergyEnabled")
    if allergy_enabled is not False:
        errors.append(
            f"drugToAllergyEnabled is {allergy_enabled}, expected false"
        )

    # --- No inhalation sigs should remain ---
    inhalation_sigs = [
        s for s in custom_sigs
        if (s.get("category") or "").lower() == "inhalation"
    ]
    if inhalation_sigs:
        inh_texts = [s.get("text", "") for s in inhalation_sigs]
        errors.append(
            f"Found {len(inhalation_sigs)} inhalation sig(s) still present: {inh_texts}"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Alert settings tightened (major-only interactions, allergy alerts off) "
        f"and inhalation sigs deleted. {len(custom_sigs)} sigs remaining."
    )
