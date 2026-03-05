import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Sertraline + Metoprolol approved, Atorvastatin denied, rest pending."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    refill_requests = state.get("refillRequests", [])
    errors = []

    checks = {
        "Sertraline": "approved",
        "Metoprolol": "approved",
        "Atorvastatin": "denied",
        "Lisinopril": "pending",
        "Gabapentin": "pending",
        "Omeprazole": "pending",
    }

    for med_name, expected_status in checks.items():
        rr = None
        for r in refill_requests:
            if med_name in (r.get("medicationName") or ""):
                rr = r
                break
        if rr is None:
            errors.append(f"No refill request found for {med_name}")
            continue

        actual_status = rr.get("status")
        if actual_status != expected_status:
            errors.append(
                f"{med_name} refill status is '{actual_status}', expected '{expected_status}'"
            )

        if expected_status in ("approved", "denied"):
            if not rr.get("processedBy"):
                errors.append(f"{med_name} refill processedBy is not set")
            if expected_status == "denied" and not rr.get("denyReason"):
                errors.append(f"{med_name} refill denyReason is not set")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Sertraline and Metoprolol refills approved, Atorvastatin denied, "
        "Lisinopril/Gabapentin/Omeprazole left pending."
    )
