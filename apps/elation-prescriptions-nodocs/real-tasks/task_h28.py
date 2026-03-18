import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    if state.get("currentPatientId") != "pat_004":
        errors.append(f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'.")

    # New Rosuvastatin prescription for pat_004
    prescriptions = state.get("prescriptions", [])
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_004"
        and "rosuvastatin" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Rosuvastatin prescription found for William Thornton (pat_004).")
    else:
        new_rx = matches[0]
        if "10mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected formStrength containing '10mg', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("quantity") != 90:
            errors.append(f"Expected quantity 90, got {new_rx.get('quantity')}.")
        if new_rx.get("daysSupply") != 90:
            errors.append(f"Expected daysSupply 90, got {new_rx.get('daysSupply')}.")
        if new_rx.get("refillsTotal") != 3:
            errors.append(f"Expected refillsTotal 3, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_005":
            errors.append(f"Expected pharmacyId 'pharm_005' (Kaiser), got '{new_rx.get('pharmacyId')}'.")

    # rr_010 (Furosemide, urgent) should be approved
    refill_requests = state.get("refillRequests", [])
    rr_010 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_010":
            rr_010 = rr
            break

    if rr_010 is None:
        errors.append("Refill request rr_010 (Furosemide) not found.")
    elif rr_010.get("status") != "approved":
        errors.append(f"Expected rr_010 status 'approved', got '{rr_010.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Rosuvastatin prescribed for William Thornton and Furosemide refill approved."
