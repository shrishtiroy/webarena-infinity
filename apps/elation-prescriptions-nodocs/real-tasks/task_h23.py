import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    # rx_014 (Apixaban) was prescribed by prov_006 (Robert Tanaka, Cardiology)
    rx_014 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_014":
            rx_014 = rx
            break

    if rx_014 is None:
        errors.append("Prescription rx_014 (Apixaban) not found.")
    else:
        if rx_014.get("refillsRemaining") != 3:
            errors.append(f"Expected rx_014 refillsRemaining 3, got {rx_014.get('refillsRemaining')}.")

    # rx_002 (Amlodipine) dosage should be 10mg
    rx_002 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_002":
            rx_002 = rx
            break

    if rx_002 is None:
        errors.append("Prescription rx_002 (Amlodipine) not found.")
    elif rx_002.get("dosage") != "10mg":
        errors.append(f"Expected rx_002 dosage '10mg', got '{rx_002.get('dosage')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Cardiologist's prescription (Apixaban) renewed with 3 refills and Amlodipine increased to 10mg."
