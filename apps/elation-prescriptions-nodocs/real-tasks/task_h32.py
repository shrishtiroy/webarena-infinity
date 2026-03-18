import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

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

    # rx_018: David Kowalski's Escitalopram — should be on-hold
    rx_018 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_018":
            rx_018 = rx
            break

    if rx_018 is None:
        errors.append("Prescription rx_018 (David's Escitalopram) not found.")
    elif rx_018.get("status") != "on-hold":
        errors.append(f"Expected rx_018 (David's Escitalopram) status 'on-hold', got '{rx_018.get('status')}'.")

    # rx_013: Margaret Chen's Sertraline — frequency should be Twice daily
    rx_013 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_013":
            rx_013 = rx
            break

    if rx_013 is None:
        errors.append("Prescription rx_013 (Margaret's Sertraline) not found.")
    elif rx_013.get("frequency") != "Twice daily":
        errors.append(f"Expected rx_013 (Margaret's Sertraline) frequency 'Twice daily', got '{rx_013.get('frequency')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "All three SSRI prescriptions updated: Aisha's increased, David's on hold, Margaret's frequency changed."
