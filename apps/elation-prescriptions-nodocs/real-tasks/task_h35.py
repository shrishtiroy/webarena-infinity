import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prescriptions = state.get("prescriptions", [])
    errors = []

    # rx_008 (Flonase / nasal spray) should be on-hold
    rx_008 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_008":
            rx_008 = rx
            break

    if rx_008 is None:
        errors.append("Prescription rx_008 (Flonase) not found.")
    elif rx_008.get("status") != "on-hold":
        errors.append(f"Expected rx_008 (Flonase) status 'on-hold', got '{rx_008.get('status')}'.")

    # rx_003 (Metformin) dosage should be 500mg
    rx_003 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_003":
            rx_003 = rx
            break

    if rx_003 is None:
        errors.append("Prescription rx_003 (Metformin) not found.")
    elif rx_003.get("dosage") != "500mg":
        errors.append(f"Expected rx_003 (Metformin) dosage '500mg', got '{rx_003.get('dosage')}'.")

    # rr_001 (Atorvastatin) should be approved
    refill_requests = state.get("refillRequests", [])
    rr_001 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_001":
            rr_001 = rr
            break

    if rr_001 is None:
        errors.append("Refill request rr_001 (Atorvastatin) not found.")
    elif rr_001.get("status") != "approved":
        errors.append(f"Expected rr_001 status 'approved', got '{rr_001.get('status')}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Flonase on hold, Metformin reduced to 500mg, Atorvastatin refill approved."
