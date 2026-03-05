import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify all PRN category custom sig shortcuts were deleted."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    custom_sigs = state.get("customSigs", [])
    errors = []

    # Check no PRN sigs remain
    prn_sigs = [s for s in custom_sigs if (s.get("category") or "").lower() == "prn"]
    if prn_sigs:
        prn_texts = [s.get("text", "") for s in prn_sigs]
        errors.append(
            f"Found {len(prn_sigs)} PRN sig(s) still present: {prn_texts}"
        )

    # Seed had 4 PRN sigs (sig_013-016) and 20 non-PRN sigs.
    # After deletion, there should be 20 sigs total.
    non_prn_count = len([s for s in custom_sigs if (s.get("category") or "").lower() != "prn"])
    if non_prn_count < 19:
        errors.append(
            f"Non-PRN sigs count is {non_prn_count}, expected at least 19 "
            f"(some non-PRN sigs may have been accidentally deleted)"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"All PRN sig shortcuts deleted. {len(custom_sigs)} sigs remaining (all non-PRN)."
    )
