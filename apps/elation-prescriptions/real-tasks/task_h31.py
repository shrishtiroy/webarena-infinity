import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify the DAW medication (Losartan) was reclassified as temporary."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    temporary_meds = state.get("temporaryMeds", [])
    errors = []

    # Losartan (the only DAW=true med) should NOT be in permanentRxMeds
    for med in permanent_rx_meds:
        if "Losartan" in (med.get("medicationName") or ""):
            errors.append(
                f"Losartan still in permanentRxMeds: '{med.get('medicationName')}'"
            )
            break

    # Losartan should be in temporaryMeds
    losartan_temp = None
    for med in temporary_meds:
        if "Losartan" in (med.get("medicationName") or ""):
            losartan_temp = med
            break

    if losartan_temp is None:
        errors.append("Losartan not found in temporaryMeds")
    else:
        if losartan_temp.get("classification") != "temporary":
            errors.append(
                f"Losartan classification is '{losartan_temp.get('classification')}', expected 'temporary'"
            )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        "Losartan (the DAW medication) reclassified from permanent Rx to temporary successfully."
    )
