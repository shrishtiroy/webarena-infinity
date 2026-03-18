import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    # rx_018: David Kowalski's Escitalopram — dosage should be 20mg
    rx_018 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_018":
            rx_018 = rx
            break

    if rx_018 is None:
        errors.append("Prescription rx_018 (David's Escitalopram) not found.")
    elif rx_018.get("dosage") != "20mg":
        errors.append(f"Expected rx_018 (David's Escitalopram) dosage '20mg', got '{rx_018.get('dosage')}'.")

    # rx_021: Aisha Rahman's Escitalopram — dosage should be 10mg
    rx_021 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_021":
            rx_021 = rx
            break

    if rx_021 is None:
        errors.append("Prescription rx_021 (Aisha's Escitalopram) not found.")
    elif rx_021.get("dosage") != "10mg":
        errors.append(f"Expected rx_021 (Aisha's Escitalopram) dosage '10mg', got '{rx_021.get('dosage')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Both Escitalopram prescriptions updated: David's to 20mg, Aisha's to 10mg."
