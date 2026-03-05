import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Ababio v. PG&E matter
    matter = next(
        (m for m in state.get("matters", [])
         if "ababio" in m.get("description", "").lower()
         and ("pacific gas" in m.get("description", "").lower()
              or "pg&e" in m.get("description", "").lower()
              or "electric" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find the Ababio v. Pacific Gas & Electric matter."

    matter_id = matter["id"]

    # Check for SF General Hospital as medical provider
    providers = [
        mp for mp in state.get("medicalProviders", [])
        if mp.get("matterId") == matter_id
    ]
    has_sf_general = any(
        mp.get("contactId") == "contact_55"
        or "sf general" in (mp.get("description", "")).lower()
        for mp in providers
    )
    if not has_sf_general:
        provider_descs = [(mp.get("contactId"), mp.get("description")) for mp in providers]
        errors.append(
            f"SF General Hospital not found as a medical provider. "
            f"Current providers: {provider_descs}."
        )

    # Check Court Case Number custom field (cf_1)
    cf = matter.get("customFields", {})
    if cf.get("cf_1") != "SF-2024-PI-8821":
        errors.append(
            f"Court Case Number is '{cf.get('cf_1')}', expected 'SF-2024-PI-8821'."
        )

    # Check settlement recovery ~$250,000
    settlements = state.get("settlements", {})
    settlement = settlements.get(matter_id, {})
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 250000) < 25000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$250,000 found. Recovery amounts: {amounts}.")

    if errors:
        return False, "Ababio v. PG&E changes not applied correctly. " + " | ".join(errors)

    return True, (
        f"Ababio v. PG&E ({matter_id}) correctly updated: "
        f"SF General Hospital added as provider, Court Case Number set, "
        f"$250,000 recovery added to settlement."
    )
