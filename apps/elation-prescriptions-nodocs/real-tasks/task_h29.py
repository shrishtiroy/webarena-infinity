import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])

    # Find new Azithromycin prescription for pat_001
    seed_ids = {f"rx_{str(i).zfill(3)}" for i in range(1, 31)}
    matches = [
        rx for rx in prescriptions
        if rx["id"] not in seed_ids
        and rx.get("patientId") == "pat_001"
        and "azithromycin" in rx.get("drugName", "").lower()
    ]

    if not matches:
        return False, "No new Azithromycin prescription found for Margaret Chen (pat_001)."

    new_rx = matches[0]
    errors = []

    if "250mg" not in new_rx.get("formStrength", "").lower().replace(" ", ""):
        errors.append(f"Expected formStrength containing '250mg', got '{new_rx.get('formStrength')}'.")

    if new_rx.get("quantity") != 6:
        errors.append(f"Expected quantity 6, got {new_rx.get('quantity')}.")

    if new_rx.get("refillsTotal") != 0:
        errors.append(f"Expected refillsTotal 0, got {new_rx.get('refillsTotal')}.")

    if new_rx.get("pharmacyId") != "pharm_001":
        errors.append(f"Expected pharmacyId 'pharm_001' (CVS), got '{new_rx.get('pharmacyId')}'.")

    if errors:
        return False, "Azithromycin prescription found but has issues: " + " ".join(errors)

    return True, "Azithromycin 250mg prescribed correctly for Margaret (avoiding Clarithromycin interaction)."
