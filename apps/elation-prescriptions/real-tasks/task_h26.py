import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Omeprazole (GERD med) refill approved with refills bumped to 5."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])
    errors = []

    # Find the Omeprazole refill request
    omeprazole_rr = None
    for rr in refill_requests:
        if "Omeprazole" in (rr.get("medicationName") or ""):
            omeprazole_rr = rr
            break

    if omeprazole_rr is None:
        errors.append("No refill request found for Omeprazole")
    else:
        if omeprazole_rr.get("status") != "approved":
            errors.append(
                f"Omeprazole refill status is '{omeprazole_rr.get('status')}', expected 'approved'"
            )
        if not omeprazole_rr.get("processedBy"):
            errors.append("Omeprazole refill processedBy is not set")
        if not omeprazole_rr.get("processedDate"):
            errors.append("Omeprazole refill processedDate is not set")

        # Check modifications include refills = 5
        mods = omeprazole_rr.get("modifications") or {}
        mod_refills = mods.get("refills")
        if mod_refills != 5:
            errors.append(
                f"Omeprazole refill modifications.refills is {mod_refills}, expected 5"
            )

    # Also check the medication's refillsRemaining was updated
    permanent_rx_meds = state.get("permanentRxMeds", [])
    omeprazole_med = None
    for med in permanent_rx_meds:
        if "Omeprazole" in (med.get("medicationName") or ""):
            omeprazole_med = med
            break

    if omeprazole_med and omeprazole_med.get("refillsRemaining") == 1:
        errors.append(
            "Omeprazole refillsRemaining is still 1, expected it to be updated to 5"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Omeprazole (GERD medication) refill approved with refills bumped to 5."
    )
