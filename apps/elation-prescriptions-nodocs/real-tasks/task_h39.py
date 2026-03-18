import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    if state.get("currentPatientId") != "pat_006":
        errors.append(f"Expected currentPatientId 'pat_006' (Robert Fitzgerald), got '{state.get('currentPatientId')}'.")

    # rx_027 (Jardiance/Empagliflozin) dosage should be 25mg
    rx_027 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_027":
            rx_027 = rx
            break

    if rx_027 is None:
        errors.append("Prescription rx_027 (Jardiance) not found.")
    elif rx_027.get("dosage") != "25mg":
        errors.append(f"Expected rx_027 (Jardiance) dosage '25mg', got '{rx_027.get('dosage')}'.")

    # rx_028 (Carvedilol) should be renewed with 5 refills
    rx_028 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_028":
            rx_028 = rx
            break

    if rx_028 is None:
        errors.append("Prescription rx_028 (Carvedilol) not found.")
    elif rx_028.get("refillsRemaining") != 5:
        errors.append(f"Expected rx_028 (Carvedilol) refillsRemaining 5, got {rx_028.get('refillsRemaining')}.")

    # rx_029 (Spironolactone) quantity should be 60
    rx_029 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_029":
            rx_029 = rx
            break

    if rx_029 is None:
        errors.append("Prescription rx_029 (Spironolactone) not found.")
    elif rx_029.get("quantity") != 60:
        errors.append(f"Expected rx_029 (Spironolactone) quantity 60, got {rx_029.get('quantity')}.")

    if errors:
        return False, " ".join(errors)

    return True, "Jardiance increased to 25mg, Carvedilol renewed with 5 refills, Spironolactone quantity increased to 60."
