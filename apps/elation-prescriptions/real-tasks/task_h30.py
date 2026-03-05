import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Amlodipine 5mg discontinued with cancel, Amlodipine 10mg prescribed."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    discontinued_meds = state.get("discontinuedMeds", [])
    canceled_scripts = state.get("canceledScripts", [])
    errors = []

    # --- Part A: Amlodipine 5mg should be discontinued ---
    aml5_in_rx = None
    for med in permanent_rx_meds:
        name = (med.get("medicationName") or "").lower()
        if "amlodipine" in name and "5mg" in name:
            aml5_in_rx = med
            break

    if aml5_in_rx is not None:
        errors.append(f"Amlodipine 5mg still in permanentRxMeds: '{aml5_in_rx.get('medicationName')}'")

    aml5_disc = None
    for med in discontinued_meds:
        name = (med.get("medicationName") or "").lower()
        if "amlodipine" in name and "5mg" in name:
            aml5_disc = med
            break

    if aml5_disc is None:
        errors.append("Amlodipine 5mg not found in discontinuedMeds")

    # --- Part A2: Cancel script should exist for Amlodipine ---
    aml_cancels = [
        cs for cs in canceled_scripts
        if "Amlodipine" in (cs.get("medicationName") or "")
    ]
    if not aml_cancels:
        errors.append("No canceled script found for Amlodipine")

    # --- Part B: Amlodipine 10mg should be in permanentRxMeds ---
    aml10_med = None
    for med in permanent_rx_meds:
        name = (med.get("medicationName") or "").lower()
        if "amlodipine" in name and "10mg" in name:
            aml10_med = med
            break

    if aml10_med is None:
        med_names = [m.get("medicationName", "") for m in permanent_rx_meds]
        errors.append(
            f"No Amlodipine 10mg found in permanentRxMeds. Current meds: {med_names}"
        )
    else:
        # Check qty
        if aml10_med.get("qty") != 30:
            errors.append(f"Amlodipine 10mg qty is {aml10_med.get('qty')}, expected 30")

        # Check refills
        if aml10_med.get("refills") != 3:
            errors.append(f"Amlodipine 10mg refills is {aml10_med.get('refills')}, expected 3")

        # Check pharmacy (should be CVS, same as the old Amlodipine 5mg)
        pharmacy_name = (aml10_med.get("pharmacyName") or "").lower()
        if "cvs" not in pharmacy_name:
            errors.append(
                f"Amlodipine 10mg pharmacy is '{aml10_med.get('pharmacyName')}', expected CVS"
            )

        # Check hypertension diagnosis
        diags = aml10_med.get("diagnosis") or []
        has_htn = any("I10" in (d.get("code") or "") for d in diags)
        if not has_htn:
            errors.append(
                f"Amlodipine 10mg missing hypertension diagnosis (I10). Diagnoses: {diags}"
            )

        # Check sig mentions once daily
        sig = (aml10_med.get("sig") or "").lower()
        if "once daily" not in sig and "daily" not in sig:
            errors.append(f"Amlodipine 10mg sig doesn't mention daily dosing: '{aml10_med.get('sig')}'")

    if errors:
        return False, " | ".join(errors)

    return True, (
        "Amlodipine 5mg discontinued with pharmacy cancel, "
        f"Amlodipine 10mg prescribed to {aml10_med.get('pharmacyName')} with I10 diagnosis."
    )
