import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Metformin 1000mg prescribed to preferred pharmacy with diabetes diagnosis."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    permanent_rx_meds = state.get("permanentRxMeds", [])
    errors = []

    # Find Metformin 1000mg in permanentRxMeds
    met1000 = None
    for med in permanent_rx_meds:
        name = (med.get("medicationName") or "").lower()
        if "metformin" in name and "1000mg" in name:
            met1000 = med
            break

    if met1000 is None:
        med_names = [m.get("medicationName", "") for m in permanent_rx_meds]
        errors.append(
            f"No Metformin 1000mg found in permanentRxMeds. Current meds: {med_names}"
        )
    else:
        # Check sig mentions twice daily
        sig = (met1000.get("sig") or "").lower()
        bid_keywords = ["twice daily", "bid", "two times daily", "2 times daily"]
        if not any(kw in sig for kw in bid_keywords):
            errors.append(f"Metformin 1000mg sig doesn't mention twice daily: '{met1000.get('sig')}'")

        # Check qty = 60
        if met1000.get("qty") != 60:
            errors.append(f"Metformin 1000mg qty is {met1000.get('qty')}, expected 60")

        # Check refills = 5
        if met1000.get("refills") != 5:
            errors.append(f"Metformin 1000mg refills is {met1000.get('refills')}, expected 5")

        # Check daysSupply = 30
        if met1000.get("daysSupply") != 30:
            errors.append(f"Metformin 1000mg daysSupply is {met1000.get('daysSupply')}, expected 30")

        # Check pharmacy is CVS (preferred)
        pharmacy_name = (met1000.get("pharmacyName") or "").lower()
        if "cvs" not in pharmacy_name:
            errors.append(
                f"Metformin 1000mg pharmacy is '{met1000.get('pharmacyName')}', expected CVS (preferred)"
            )

        # Check diabetes diagnosis (E11.9)
        diags = met1000.get("diagnosis") or []
        has_dm = any("E11" in (d.get("code") or "") for d in diags)
        if not has_dm:
            errors.append(
                f"Metformin 1000mg missing diabetes diagnosis (E11.9). Diagnoses: {diags}"
            )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Metformin 1000mg prescribed: sig='{met1000.get('sig')}', qty={met1000.get('qty')}, "
        f"refills={met1000.get('refills')}, daysSupply={met1000.get('daysSupply')}, "
        f"pharmacy='{met1000.get('pharmacyName')}', diagnosis includes diabetes."
    )
