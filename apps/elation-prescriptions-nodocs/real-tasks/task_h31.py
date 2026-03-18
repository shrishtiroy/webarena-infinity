import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    if state.get("currentPatientId") != "pat_004":
        errors.append(f"Expected currentPatientId 'pat_004' (William Thornton), got '{state.get('currentPatientId')}'.")

    # rx_023 (Insulin Glargine, has prior auth) — dosage should be 30 units, renewed with 5
    rx_023 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_023":
            rx_023 = rx
            break

    if rx_023 is None:
        errors.append("Prescription rx_023 (Insulin Glargine) not found.")
    else:
        if rx_023.get("dosage") != "30 units":
            errors.append(f"Expected rx_023 dosage '30 units', got '{rx_023.get('dosage')}'.")
        if rx_023.get("refillsRemaining") != 5:
            errors.append(f"Expected rx_023 refillsRemaining 5, got {rx_023.get('refillsRemaining')}.")

    # rx_024 (Furosemide) — quantity should be 60
    rx_024 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_024":
            rx_024 = rx
            break

    if rx_024 is None:
        errors.append("Prescription rx_024 (Furosemide) not found.")
    elif rx_024.get("quantity") != 60:
        errors.append(f"Expected rx_024 quantity 60, got {rx_024.get('quantity')}.")

    if errors:
        return False, " ".join(errors)

    return True, "Insulin dosage increased to 30 units, renewed with 5 refills, Furosemide quantity increased to 60."
