import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    if state.get("currentPatientId") != "pat_002":
        errors.append(f"Expected currentPatientId 'pat_002' (David Kowalski), got '{state.get('currentPatientId')}'.")

    prescriptions = state.get("prescriptions", [])
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_002"
        and "apixaban" in rx.get("drugName", "").lower()
    ]

    if not matches:
        errors.append("No new Apixaban prescription found for David Kowalski (pat_002).")
    else:
        new_rx = matches[0]
        if "5mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
            errors.append(f"Expected formStrength containing '5mg', got '{new_rx.get('formStrength')}'.")
        if new_rx.get("frequency") != "Twice daily":
            errors.append(f"Expected frequency 'Twice daily', got '{new_rx.get('frequency')}'.")
        if new_rx.get("quantity") != 60:
            errors.append(f"Expected quantity 60, got {new_rx.get('quantity')}.")
        if new_rx.get("refillsTotal") != 5:
            errors.append(f"Expected refillsTotal 5, got {new_rx.get('refillsTotal')}.")
        if new_rx.get("daw") is not True:
            errors.append(f"Expected daw True, got {new_rx.get('daw')}.")
        if new_rx.get("priorAuth") is not True:
            errors.append(f"Expected priorAuth True, got {new_rx.get('priorAuth')}.")
        if new_rx.get("priorAuthNumber") != "PA-2026-DK-001":
            errors.append(f"Expected priorAuthNumber 'PA-2026-DK-001', got '{new_rx.get('priorAuthNumber')}'.")
        if new_rx.get("pharmacyId") != "pharm_003":
            errors.append(f"Expected pharmacyId 'pharm_003' (Rite Aid), got '{new_rx.get('pharmacyId')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Apixaban 5mg prescribed for David Kowalski with DAW and prior auth correctly."
