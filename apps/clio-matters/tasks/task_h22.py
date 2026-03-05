import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the two Doyle PI matters
    doyle_matters = [
        m for m in state.get("matters", [])
        if "doyle" in m.get("description", "").lower()
        and m.get("practiceAreaId") == "pa_1"
    ]

    if len(doyle_matters) < 2:
        return False, f"Expected at least 2 Doyle PI matters, found {len(doyle_matters)}."

    # Sort by open date to find the more recently opened one
    doyle_matters.sort(key=lambda m: m.get("openDate", ""))
    newer_matter = doyle_matters[-1]
    matter_id = newer_matter["id"]

    # Check responsible attorney changed to Marcus Williams (user_2)
    if newer_matter.get("responsibleAttorneyId") != "user_2":
        errors.append(
            f"Newer Doyle matter ({matter_id}, '{newer_matter.get('description', '')}') "
            f"has responsibleAttorneyId '{newer_matter.get('responsibleAttorneyId')}', "
            f"expected 'user_2' (Marcus Williams)."
        )

    # Check for new special damage ~$5,000
    damages = state.get("damages", [])
    matter_damages = [d for d in damages if d.get("matterId") == matter_id]
    has_er_damage = any(
        d.get("type") == "special" and abs(float(d.get("amount", 0)) - 5000) < 1000
        for d in matter_damages
    )
    if not has_er_damage:
        existing = [(d.get("name"), d.get("amount"), d.get("type")) for d in matter_damages]
        errors.append(
            f"No special damage with amount close to $5,000 found on newer Doyle matter "
            f"({matter_id}). Existing damages: {existing}."
        )

    if errors:
        return False, "Newer Doyle matter not updated correctly. " + " | ".join(errors)

    return True, (
        f"Newer Doyle PI matter ({matter_id}, '{newer_matter.get('description', '')}') "
        f"has Marcus Williams as attorney and a ~$5,000 special damage added."
    )
