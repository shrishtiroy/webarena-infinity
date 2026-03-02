import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Doyle scaffolding case
    doyle = next(
        (m for m in state.get("matters", [])
         if "doyle" in m.get("description", "").lower()
         and ("scaffolding" in m.get("description", "").lower()
              or "summit" in m.get("description", "").lower())),
        None,
    )
    if doyle is None:
        return False, "Doyle scaffolding fall case not found."

    # Find Washington workplace crush injury case
    washington = next(
        (m for m in state.get("matters", [])
         if "washington" in m.get("description", "").lower()
         and "pacific steel" in m.get("description", "").lower()),
        None,
    )
    if washington is None:
        return False, "Washington workplace crush injury case not found."

    providers = state.get("medicalProviders", [])

    # Check Pacific Physical Therapy Center (contact_57) on Doyle case
    doyle_has_ppt = any(
        p.get("matterId") == doyle["id"]
        and (p.get("contactId") == "contact_57"
             or "pacific physical" in p.get("description", "").lower())
        for p in providers
    )
    if not doyle_has_ppt:
        doyle_provs = [
            (p.get("contactId"), p.get("description"))
            for p in providers if p.get("matterId") == doyle["id"]
        ]
        errors.append(
            f"Pacific Physical Therapy Center not found on Doyle case. "
            f"Providers: {doyle_provs}."
        )

    # Check Pacific Physical Therapy Center (contact_57) on Washington case
    wash_has_ppt = any(
        p.get("matterId") == washington["id"]
        and (p.get("contactId") == "contact_57"
             or "pacific physical" in p.get("description", "").lower())
        for p in providers
    )
    if not wash_has_ppt:
        wash_provs = [
            (p.get("contactId"), p.get("description"))
            for p in providers if p.get("matterId") == washington["id"]
        ]
        errors.append(
            f"Pacific Physical Therapy Center not found on Washington case. "
            f"Providers: {wash_provs}."
        )

    if errors:
        return False, (
            "Pacific Physical Therapy not added to both matters. " + " | ".join(errors)
        )

    return True, (
        "Pacific Physical Therapy Center correctly added as medical provider "
        "to both the Doyle scaffolding and Washington workplace cases."
    )
