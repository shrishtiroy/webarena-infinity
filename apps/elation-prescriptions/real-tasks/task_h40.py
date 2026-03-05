import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Doxycycline 100mg template created and matching oral sig shortcut added."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    rx_templates = state.get("rxTemplates", [])
    custom_sigs = state.get("customSigs", [])
    errors = []

    # --- Part A: Doxycycline 100mg template ---
    doxy_tpl = None
    for tpl in rx_templates:
        name = (tpl.get("medicationName") or "").lower()
        if "doxycycline" in name and "100mg" in name:
            doxy_tpl = tpl
            break

    if doxy_tpl is None:
        tpl_names = [t.get("medicationName", "") for t in rx_templates]
        errors.append(
            f"No Doxycycline 100mg template found. Current templates: {tpl_names}"
        )
    else:
        # Check sig mentions twice daily
        sig = (doxy_tpl.get("sig") or "").lower()
        if "twice daily" not in sig and "bid" not in sig:
            errors.append(f"Doxycycline template sig doesn't mention twice daily: '{doxy_tpl.get('sig')}'")

        if doxy_tpl.get("qty") != 28:
            errors.append(f"Doxycycline template qty is {doxy_tpl.get('qty')}, expected 28")

        unit = (doxy_tpl.get("unit") or "").lower()
        if unit != "capsules":
            errors.append(f"Doxycycline template unit is '{doxy_tpl.get('unit')}', expected 'capsules'")

        if doxy_tpl.get("refills") != 0:
            errors.append(f"Doxycycline template refills is {doxy_tpl.get('refills')}, expected 0")

        if doxy_tpl.get("daysSupply") != 14:
            errors.append(f"Doxycycline template daysSupply is {doxy_tpl.get('daysSupply')}, expected 14")

    # --- Part B: Matching custom sig shortcut in oral category ---
    doxy_sig = None
    for sig in custom_sigs:
        text = (sig.get("text") or "").lower()
        cat = (sig.get("category") or "").lower()
        if cat == "oral" and "twice daily" in text and "14 days" in text:
            doxy_sig = sig
            break

    if doxy_sig is None:
        errors.append(
            "No oral sig shortcut found containing 'twice daily' and '14 days'"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, (
        f"Doxycycline 100mg template created (sig='{doxy_tpl.get('sig')}', qty={doxy_tpl.get('qty')}, "
        f"refills={doxy_tpl.get('refills')}, daysSupply={doxy_tpl.get('daysSupply')}) "
        f"and matching oral sig shortcut added: '{doxy_sig.get('text')}'."
    )
