import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find open matter with highest WIP (should be TechNova at $35,200)
    best_matter = None
    best_wip = -1
    for m in state.get("matters", []):
        if m.get("status") == "Open":
            wip = m.get("financials", {}).get("workInProgress", 0)
            if wip > best_wip:
                best_wip = wip
                best_matter = m

    if not best_matter:
        return False, "No open matters found."

    thompson = next(
        (u for u in state.get("firmUsers", [])
         if u.get("fullName") == "Rachel Thompson"),
        None,
    )
    garcia = next(
        (u for u in state.get("firmUsers", [])
         if u.get("fullName") == "Maria Garcia"),
        None,
    )
    if not thompson or not garcia:
        return False, "Rachel Thompson or Maria Garcia not found."

    errors = []
    if best_matter.get("responsibleStaffId") != thompson["id"]:
        errors.append(
            f"Responsible staff is '{best_matter.get('responsibleStaffId')}', "
            f"expected '{thompson['id']}' (Rachel Thompson)."
        )
    if best_matter.get("originatingAttorneyId") != garcia["id"]:
        errors.append(
            f"Originating attorney is '{best_matter.get('originatingAttorneyId')}', "
            f"expected '{garcia['id']}' (Maria Garcia)."
        )

    if errors:
        desc = best_matter.get("description") or best_matter.get("id")
        return False, f"'{desc}': " + " ".join(errors)

    desc = best_matter.get("description") or best_matter.get("id")
    return True, f"'{desc}' (highest WIP): staff=Thompson, originating=Garcia."
