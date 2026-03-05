import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify CVS refills: approve those with refills remaining, deny the one with 0."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])
    errors = []

    # CVS pending refills in seed: Lisinopril(2 rem), Atorvastatin(4 rem),
    # Gabapentin(0 rem), Omeprazole(1 rem), Metoprolol(2 rem)
    should_approve = ["Lisinopril", "Atorvastatin", "Omeprazole", "Metoprolol"]
    should_deny = ["Gabapentin"]

    for med_name in should_approve:
        rr = None
        for r in refill_requests:
            if med_name in (r.get("medicationName") or ""):
                rr = r
                break
        if rr is None:
            errors.append(f"No refill request found for {med_name}")
        elif rr.get("status") != "approved":
            errors.append(f"{med_name} refill status is '{rr.get('status')}', expected 'approved'")
        elif not rr.get("processedBy"):
            errors.append(f"{med_name} refill processedBy is not set")

    for med_name in should_deny:
        rr = None
        for r in refill_requests:
            if med_name in (r.get("medicationName") or ""):
                rr = r
                break
        if rr is None:
            errors.append(f"No refill request found for {med_name}")
        elif rr.get("status") != "denied":
            errors.append(f"{med_name} refill status is '{rr.get('status')}', expected 'denied'")
        elif not rr.get("denyReason"):
            errors.append(f"{med_name} refill denyReason is not set")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "All CVS refills processed correctly: Lisinopril, Atorvastatin, Omeprazole, "
        "Metoprolol approved; Gabapentin (0 refills remaining) denied."
    )
