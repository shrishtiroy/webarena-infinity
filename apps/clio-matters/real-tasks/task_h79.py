import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find open matter with second-highest trust fund balance
    open_matters = [
        m for m in state.get("matters", [])
        if m.get("status") == "Open"
    ]
    if len(open_matters) < 2:
        return False, "Not enough open matters to find second-highest."

    sorted_by_trust = sorted(
        open_matters,
        key=lambda m: m.get("financials", {}).get("trustFunds", 0),
        reverse=True,
    )
    target = sorted_by_trust[1]  # second highest

    thompson = next(
        (u for u in state.get("firmUsers", [])
         if u.get("fullName") == "Rachel Thompson"),
        None,
    )
    if not thompson:
        return False, "Rachel Thompson not found."

    errors = []
    if target.get("billingPreference", {}).get("billingMethod") != "flat_rate":
        errors.append(
            f"Billing is '{target.get('billingPreference', {}).get('billingMethod')}', "
            f"expected 'flat_rate'."
        )
    if target.get("responsibleStaffId") != thompson["id"]:
        errors.append(
            f"Responsible staff is '{target.get('responsibleStaffId')}', "
            f"expected '{thompson['id']}' (Rachel Thompson)."
        )

    if errors:
        desc = target.get("description") or target.get("id")
        return False, f"'{desc}': " + " ".join(errors)

    desc = target.get("description") or target.get("id")
    return True, f"'{desc}' (2nd highest trust): billing=flat_rate, staff=Thompson."
