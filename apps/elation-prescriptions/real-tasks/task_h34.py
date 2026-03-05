import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Sertraline discontinued and Escitalopram 10mg prescribed to Walgreens."""
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

    # --- Part A: Sertraline should be discontinued ---
    for med in permanent_rx_meds:
        if "Sertraline" in (med.get("medicationName") or ""):
            errors.append(f"Sertraline still in permanentRxMeds: '{med.get('medicationName')}'")
            break

    sert_disc = None
    for med in discontinued_meds:
        if "Sertraline" in (med.get("medicationName") or ""):
            sert_disc = med
            break

    if sert_disc is None:
        errors.append("Sertraline not found in discontinuedMeds")

    # --- Part B: Escitalopram 10mg should be prescribed ---
    escit_med = None
    for med in permanent_rx_meds:
        name = (med.get("medicationName") or "").lower()
        if "escitalopram" in name and "10mg" in name:
            escit_med = med
            break

    if escit_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_rx_meds]
        errors.append(
            f"No Escitalopram 10mg found in permanentRxMeds. Current meds: {med_names}"
        )
    else:
        # Check sig mentions once daily / morning
        sig = (escit_med.get("sig") or "").lower()
        if "daily" not in sig:
            errors.append(f"Escitalopram sig doesn't mention daily: '{escit_med.get('sig')}'")

        # Check qty = 30
        if escit_med.get("qty") != 30:
            errors.append(f"Escitalopram qty is {escit_med.get('qty')}, expected 30")

        # Check refills = 5
        if escit_med.get("refills") != 5:
            errors.append(f"Escitalopram refills is {escit_med.get('refills')}, expected 5")

        # Check pharmacy is Walgreens (where Sertraline was)
        pharmacy_name = (escit_med.get("pharmacyName") or "").lower()
        if "walgreens" not in pharmacy_name:
            errors.append(
                f"Escitalopram pharmacy is '{escit_med.get('pharmacyName')}', expected Walgreens"
            )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Sertraline discontinued and Escitalopram 10mg prescribed to "
        f"{escit_med.get('pharmacyName')} successfully."
    )
