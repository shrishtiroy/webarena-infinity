import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # Patient with ACE inhibitor allergy is William Thornton (pat_004)
    if state.get("currentPatientId") != "pat_004":
        errors.append(f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'.")

    prescriptions = state.get("prescriptions", [])
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_004"
        and "amlodipine" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Amlodipine prescription found for William Thornton (pat_004).")
    else:
        new_rx = matches[0]
        if "10mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected formStrength containing '10mg', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("frequency") != "Once daily":
            errors.append(f"Expected frequency 'Once daily', got '{new_rx.get('frequency')}'.")
        if new_rx.get("quantity") != 30:
            errors.append(f"Expected quantity 30, got {new_rx.get('quantity')}.")
        if new_rx.get("refillsTotal") != 5:
            errors.append(f"Expected refillsTotal 5, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("pharmacyId") != "pharm_005":
            errors.append(f"Expected pharmacyId 'pharm_005' (Kaiser), got '{new_rx.get('pharmacyId')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Amlodipine 10mg prescribed for William Thornton (ACE inhibitor allergy patient)."
