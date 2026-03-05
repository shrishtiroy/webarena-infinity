import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify both change requests (statin swap and sig clarification) were approved."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    change_requests = state.get("changeRequests", [])
    errors = []

    # --- CR1: Atorvastatin→Rosuvastatin therapeutic substitution ---
    cr1 = None
    for cr in change_requests:
        if "Atorvastatin" in (cr.get("originalMedication") or ""):
            cr1 = cr
            break

    if cr1 is None:
        errors.append("No change request found for Atorvastatin→Rosuvastatin")
    else:
        if cr1.get("status") != "approved":
            errors.append(
                f"Atorvastatin change request status is '{cr1.get('status')}', expected 'approved'"
            )
        if not cr1.get("processedBy"):
            errors.append("Atorvastatin change request processedBy is not set")
        if not cr1.get("processedDate"):
            errors.append("Atorvastatin change request processedDate is not set")

    # --- CR2: Gabapentin sig clarification ---
    cr2 = None
    for cr in change_requests:
        if "Gabapentin" in (cr.get("medicationName") or ""):
            cr2 = cr
            break

    if cr2 is None:
        errors.append("No change request found for Gabapentin sig clarification")
    else:
        if cr2.get("status") != "approved":
            errors.append(
                f"Gabapentin change request status is '{cr2.get('status')}', expected 'approved'"
            )
        if not cr2.get("processedBy"):
            errors.append("Gabapentin change request processedBy is not set")
        if not cr2.get("processedDate"):
            errors.append("Gabapentin change request processedDate is not set")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, "Both change requests approved: Atorvastatin→Rosuvastatin and Gabapentin sig clarification."
