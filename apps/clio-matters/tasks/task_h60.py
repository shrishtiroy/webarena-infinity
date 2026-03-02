import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Washington v. Pacific Steel matter
    matter = next(
        (m for m in state.get("matters", [])
         if "washington" in m.get("description", "").lower()
         and "pacific steel" in m.get("description", "").lower()),
        None
    )
    if matter is None:
        return False, "Could not find the Washington v. Pacific Steel matter."

    matter_id = matter["id"]

    # Check currency is CAD
    billing = matter.get("billing", {})
    if billing.get("currency") != "CAD":
        errors.append(
            f"Billing currency is '{billing.get('currency')}', expected 'CAD'."
        )

    # Check for UCSF Medical Center as related contact (Medical Provider relationship)
    relationships = matter.get("relationships", [])
    has_ucsf = any(
        r.get("contactId") == "contact_59"
        and "medical provider" in r.get("relationship", "").lower()
        for r in relationships
    )
    if not has_ucsf:
        # Also check by name in case contactId differs
        has_ucsf_alt = any(
            "medical provider" in r.get("relationship", "").lower()
            for r in relationships
            if r.get("contactId") == "contact_59"
        )
        if not has_ucsf_alt:
            rel_info = [(r.get("contactId"), r.get("relationship")) for r in relationships]
            errors.append(
                f"UCSF Medical Center not found as a Medical Provider related contact. "
                f"Current relationships: {rel_info}."
            )

    # Check settlement lien ~$30,000 from CalComp
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})
    liens = settlement.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 30000) < 5000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(
            f"No non-medical lien ~$30,000 found. Lien amounts: {lien_amounts}."
        )

    if errors:
        return False, "Washington v. Pacific Steel changes not applied correctly. " + " | ".join(errors)

    return True, (
        f"Washington v. Pacific Steel ({matter_id}) correctly updated: "
        f"currency changed to CAD, UCSF Medical Center added as related contact, "
        f"$30,000 CalComp lien added to settlement."
    )
