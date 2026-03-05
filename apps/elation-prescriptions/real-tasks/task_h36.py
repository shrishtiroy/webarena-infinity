import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Gabapentin Rx template created from active medication details."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    rx_templates = state.get("rxTemplates", [])
    errors = []

    # Find a Gabapentin template
    gaba_tpl = None
    for tpl in rx_templates:
        if "Gabapentin" in (tpl.get("medicationName") or "") and "300mg" in (tpl.get("medicationName") or ""):
            gaba_tpl = tpl
            break

    if gaba_tpl is None:
        tpl_names = [t.get("medicationName", "") for t in rx_templates]
        errors.append(
            f"No Gabapentin 300mg template found. Current templates: {tpl_names}"
        )
    else:
        # Should match active med: sig="Take 1 capsule by mouth three times daily",
        # qty=90, unit=capsules, refills=2, daysSupply=30
        sig = (gaba_tpl.get("sig") or "").lower()
        if "three times daily" not in sig and "tid" not in sig and "3 times" not in sig:
            errors.append(
                f"Gabapentin template sig doesn't match active med's TID dosing: '{gaba_tpl.get('sig')}'"
            )

        if gaba_tpl.get("qty") != 90:
            errors.append(f"Gabapentin template qty is {gaba_tpl.get('qty')}, expected 90")

        unit = (gaba_tpl.get("unit") or "").lower()
        if unit != "capsules":
            errors.append(f"Gabapentin template unit is '{gaba_tpl.get('unit')}', expected 'capsules'")

        if gaba_tpl.get("refills") != 2:
            errors.append(f"Gabapentin template refills is {gaba_tpl.get('refills')}, expected 2")

        if gaba_tpl.get("daysSupply") != 30:
            errors.append(f"Gabapentin template daysSupply is {gaba_tpl.get('daysSupply')}, expected 30")

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Gabapentin 300mg template created from active medication: "
        f"sig='{gaba_tpl.get('sig')}', qty={gaba_tpl.get('qty')}, "
        f"unit={gaba_tpl.get('unit')}, refills={gaba_tpl.get('refills')}, "
        f"daysSupply={gaba_tpl.get('daysSupply')}."
    )
