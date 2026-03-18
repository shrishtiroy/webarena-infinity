import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    rx_004 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_004":
            rx_004 = rx
            break

    if rx_004 is None:
        return False, "Prescription rx_004 (Levothyroxine) not found."

    if rx_004.get("dosage") != "88mcg":
        errors.append(f"Expected dosage '88mcg', got '{rx_004.get('dosage')}'.")

    expected_sig = "Take 1 tablet by mouth once daily on an empty stomach, 60 minutes before breakfast"
    if rx_004.get("sig") != expected_sig:
        errors.append(f"Expected sig to be updated, got '{rx_004.get('sig')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Levothyroxine dosage increased to 88mcg with updated directions."
