import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settlements = state.get("settlements", {})
    matter_1_settlement = settlements.get("matter_1")

    if matter_1_settlement is None:
        return False, "No settlement found for matter_1."

    non_medical_liens = matter_1_settlement.get("nonMedicalLiens", [])
    target = None
    for nml in non_medical_liens:
        if nml.get("holderContactId") == "contact_42":
            target = nml
            break

    if target is None:
        return False, (
            "No non-medical lien with holderContactId 'contact_42' (CalComp Workers Compensation) "
            f"found in matter_1 settlement. Existing liens: {non_medical_liens}"
        )

    description = (target.get("description") or "").lower()
    if "workers compensation" not in description and "workers' compensation" not in description:
        return False, (
            f"Non-medical lien description '{target.get('description')}' does not contain "
            "'Workers compensation lien'."
        )

    amount = target.get("amount")
    if amount != 15000:
        return False, f"Non-medical lien amount is {amount}, expected 15000."

    reduction = target.get("reduction")
    if reduction != 3000:
        return False, f"Non-medical lien reduction is {reduction}, expected 3000."

    return True, "Non-medical lien from contact_42 (CalComp Workers Compensation) correctly added with amount 15000 and reduction 3000."
