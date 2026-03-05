import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Atorvastatin→Rosuvastatin change request approved AND Atorvastatin discontinued."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    change_requests = state.get("changeRequests", [])
    permanent_rx_meds = state.get("permanentRxMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    errors = []

    # --- Part A: Change request for Atorvastatin→Rosuvastatin approved ---
    cr = None
    for req in change_requests:
        if "Atorvastatin" in (req.get("originalMedication") or ""):
            cr = req
            break

    if cr is None:
        errors.append("No change request found for Atorvastatin")
    else:
        if cr.get("status") != "approved":
            errors.append(f"Change request status is '{cr.get('status')}', expected 'approved'")
        if not cr.get("processedBy"):
            errors.append("Change request processedBy is not set")
        if not cr.get("processedDate"):
            errors.append("Change request processedDate is not set")

    # --- Part B: Atorvastatin should NOT be in permanentRxMeds ---
    for med in permanent_rx_meds:
        if "Atorvastatin" in (med.get("medicationName") or ""):
            errors.append(f"Atorvastatin still in permanentRxMeds: '{med.get('medicationName')}'")
            break

    # --- Part C: Atorvastatin should be in discontinuedMeds ---
    atorvastatin_disc = None
    for med in discontinued_meds:
        if "Atorvastatin" in (med.get("medicationName") or ""):
            atorvastatin_disc = med
            break

    if atorvastatin_disc is None:
        errors.append("Atorvastatin not found in discontinuedMeds")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Atorvastatin→Rosuvastatin change request approved and Atorvastatin discontinued successfully."
    )
