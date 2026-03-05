import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify med rec completed, Prednisone + Ciprofloxacin discontinued, Amoxicillin kept."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    temporary_meds = state.get("temporaryMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    patient = state.get("currentPatient", {})
    errors = []

    # --- Med rec should be completed ---
    last_reconciled = patient.get("lastReconciledDate", "")
    if not last_reconciled or last_reconciled == "2026-01-15T14:30:00Z":
        errors.append(
            "lastReconciledDate not updated (still seed value or empty)"
        )

    # --- Prednisone should be discontinued ---
    for med in temporary_meds:
        if "Prednisone" in (med.get("medicationName") or ""):
            errors.append(f"Prednisone still in temporaryMeds: '{med.get('medicationName')}'")
            break

    pred_disc = None
    for med in discontinued_meds:
        if "Prednisone" in (med.get("medicationName") or ""):
            pred_disc = med
            break

    if pred_disc is None:
        errors.append("Prednisone not found in discontinuedMeds")

    # --- Ciprofloxacin should be discontinued ---
    for med in temporary_meds:
        if "Ciprofloxacin" in (med.get("medicationName") or ""):
            errors.append(f"Ciprofloxacin still in temporaryMeds: '{med.get('medicationName')}'")
            break

    cipro_disc = None
    for med in discontinued_meds:
        if "Ciprofloxacin" in (med.get("medicationName") or ""):
            cipro_disc = med
            break

    if cipro_disc is None:
        errors.append("Ciprofloxacin not found in discontinuedMeds")

    # --- Amoxicillin should still be in temporaryMeds ---
    amox_found = False
    for med in temporary_meds:
        if "Amoxicillin" in (med.get("medicationName") or ""):
            amox_found = True
            break

    if not amox_found:
        errors.append("Amoxicillin should still be in temporaryMeds but was not found")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Medication reconciliation completed. Prednisone and Ciprofloxacin discontinued "
        "(expired courses), Amoxicillin retained (still active)."
    )
