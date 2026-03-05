import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check for Maritime Law practice area
    maritime_pa = next(
        (pa for pa in state.get("practiceAreas", [])
         if "maritime" in pa.get("name", "").lower()),
        None
    )
    if maritime_pa is None:
        return False, "No 'Maritime Law' practice area found."

    pa_id = maritime_pa["id"]

    # Check stages
    stages = maritime_pa.get("stages", [])
    stage_names = [s.get("name", "").lower() for s in stages]
    for expected in ["investigation", "filing", "arbitration"]:
        if not any(expected in sn for sn in stage_names):
            errors.append(f"Missing stage '{expected}' in Maritime Law. Found: {[s.get('name') for s in stages]}.")

    # Check for new matter under Maritime Law for Andrew Kim
    kim_matter = next(
        (m for m in state.get("matters", [])
         if m.get("practiceAreaId") == pa_id
         and ("kim" in m.get("description", "").lower()
              or m.get("clientId") == "contact_43")),
        None
    )
    if kim_matter is None:
        # Try finding by client
        kim_matter = next(
            (m for m in state.get("matters", [])
             if m.get("clientId") == "contact_43"
             and m.get("practiceAreaId") == pa_id),
            None
        )

    if kim_matter is None:
        errors.append("No matter found under Maritime Law for client Andrew Kim.")
    else:
        if kim_matter.get("billingMethod") != "hourly" and kim_matter.get("billing", {}).get("method") != "hourly":
            errors.append(
                f"Kim matter billing is '{kim_matter.get('billingMethod')}', expected 'hourly'."
            )
        if "maritime" not in kim_matter.get("description", "").lower() and "shipping" not in kim_matter.get("description", "").lower():
            errors.append(
                f"Kim matter description '{kim_matter.get('description')}' doesn't reference maritime/shipping."
            )

    if errors:
        return False, "Maritime Law setup not complete. " + " | ".join(errors)

    return True, (
        f"Maritime Law practice area created with stages {[s.get('name') for s in stages]}, "
        f"and Kim Maritime matter created with hourly billing."
    )
