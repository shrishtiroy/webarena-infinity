import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    errors = []

    # rx_014 (Apixaban/Eliquis — blood thinner with prior auth) quantity should be 90
    prescriptions = state.get("prescriptions", [])
    rx_014 = None
    for rx in prescriptions:
        if rx.get("id") == "rx_014":
            rx_014 = rx
            break

    if rx_014 is None:
        errors.append("Prescription rx_014 (Apixaban) not found.")
    elif rx_014.get("quantity") != 90:
        errors.append(f"Expected rx_014 (Apixaban) quantity 90, got {rx_014.get('quantity')}.")

    # rr_011 (Sertraline refill) should be denied with reason containing "changed"
    refill_requests = state.get("refillRequests", [])
    rr_011 = None
    for rr in refill_requests:
        if rr.get("id") == "rr_011":
            rr_011 = rr
            break

    if rr_011 is None:
        errors.append("Refill request rr_011 (Sertraline) not found.")
    else:
        if rr_011.get("status") != "denied":
            errors.append(f"Expected rr_011 status 'denied', got '{rr_011.get('status')}'.")
        deny_reason = str(rr_011.get("denyReason", ""))
        if "changed" not in deny_reason.lower():
            errors.append(f"Expected rr_011 denyReason to contain 'changed', got '{deny_reason}'.")

    if errors:
        return False, " ".join(errors)

    return True, "Apixaban quantity increased to 90 and Sertraline refill denied (therapy changed)."
