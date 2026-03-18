import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_012 (Hydrochlorothiazide, on-hold diuretic) should be resumed
    prescriptions = state.get("prescriptions", [])
    rx_012 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_012":
            rx_012 = rx
            break

    if rx_012 is None:
        errors.append("Prescription rx_012 (Hydrochlorothiazide) not found.")
    elif rx_012.get("status") != "active":
        errors.append(f"Expected rx_012 (HCTZ) status 'active', got '{rx_012.get('status')}'.")

    # rr_003 (Pantoprazole, urgent) should be modified-and-approved
    refill_requests = state.get("refillRequests", [])
    rr_003 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_003":
            rr_003 = rr
            break

    if rr_003 is None:
        errors.append("Refill request rr_003 (Pantoprazole) not found.")
    else:
        if rr_003.get("status") != "modified":
            errors.append(f"Expected rr_003 status 'modified', got '{rr_003.get('status')}'.")
        details = str(rr_003.get("modifiedDetails", ""))
        if not details:
            errors.append("Expected rr_003 modifiedDetails to contain modification note, but got empty.")

    if errors:
        return False, " ".join(errors)

    return True, "Diuretic resumed and urgent Pantoprazole refill modified-and-approved."
