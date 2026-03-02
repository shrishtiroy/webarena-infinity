import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Doyle scaffolding fall case
    matter = next(
        (m for m in state.get("matters", [])
         if "doyle" in m.get("description", "").lower()
         and ("scaffolding" in m.get("description", "").lower()
              or "summit" in m.get("description", "").lower())),
        None,
    )
    if matter is None:
        return False, "Doyle scaffolding fall case not found."

    matter_id = matter["id"]

    # 1. Check $20,000 special damage for shoulder surgery
    damages = [d for d in state.get("damages", []) if d.get("matterId") == matter_id]
    has_damage = any(
        abs(float(d.get("amount", 0)) - 20000) < 2000
        and "shoulder" in d.get("name", "").lower()
        for d in damages
    )
    if not has_damage:
        dam_list = [(d.get("name"), d.get("amount")) for d in damages]
        errors.append(
            f"No $20,000 shoulder surgery damage found. Damages: {dam_list}."
        )

    # 2. Check Bay Area Orthopedic Associates as medical provider
    providers = [
        p for p in state.get("medicalProviders", [])
        if p.get("matterId") == matter_id
    ]
    has_provider = any(
        p.get("contactId") == "contact_56"
        or "bay area orthopedic" in p.get("description", "").lower()
        for p in providers
    )
    if not has_provider:
        prov_list = [(p.get("contactId"), p.get("description")) for p in providers]
        errors.append(
            f"Bay Area Orthopedic Associates not found as provider. Providers: {prov_list}."
        )

    # 3. Check $100,000 recovery from Summit Construction Insurance in settlement
    settlement = state.get("settlements", {}).get(matter_id, {})
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 100000) < 10000
        for r in recoveries
    )
    if not has_recovery:
        rec_amounts = [r.get("amount") for r in recoveries]
        errors.append(
            f"No $100,000 recovery found in settlement. Recoveries: {rec_amounts}."
        )

    if errors:
        return False, (
            "Doyle scaffolding case cross-tab updates not complete. " + " | ".join(errors)
        )

    return True, (
        "Doyle scaffolding case correctly updated across all three tabs: "
        "$20,000 shoulder surgery damage, Bay Area Orthopedic provider, "
        "$100,000 recovery from Summit Construction."
    )
