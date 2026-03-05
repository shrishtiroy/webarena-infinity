import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Losartan (prescribed by another provider) was discontinued."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    errors = []

    # Losartan should NOT be in permanentRxMeds
    for med in permanent_rx_meds:
        if "Losartan" in (med.get("medicationName") or ""):
            errors.append(f"Losartan still in permanentRxMeds: '{med.get('medicationName')}'")
            break

    # Losartan should be in discontinuedMeds
    losartan_disc = None
    for med in discontinued_meds:
        if "Losartan" in (med.get("medicationName") or ""):
            losartan_disc = med
            break

    if losartan_disc is None:
        errors.append("Losartan not found in discontinuedMeds")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Losartan (prescribed by another provider) discontinued successfully. "
        f"Reason: '{losartan_disc.get('discontinueReason', 'N/A')}'."
    )
