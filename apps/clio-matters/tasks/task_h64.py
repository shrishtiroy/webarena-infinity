import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # 1. Check Admiralty Law practice area
    admiralty = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("name", "").lower() == "admiralty law"),
        None,
    )
    if admiralty is None:
        return False, "Practice area 'Admiralty Law' not found."

    stage_names = [s["name"] for s in admiralty.get("stages", [])]
    for expected in ["Pre-Filing", "Discovery", "Trial"]:
        if not any(expected.lower() == s.lower() for s in stage_names):
            errors.append(f"Stage '{expected}' not found in Admiralty Law. Stages: {stage_names}.")

    # 2. Check template
    template = next(
        (t for t in state.get("matterTemplates", [])
         if "admiralty" in t.get("name", "").lower()
         and "cargo" in t.get("name", "").lower()),
        None,
    )
    if template is None:
        errors.append("Template 'Admiralty - Cargo Dispute' not found.")
    else:
        if template.get("practiceAreaId") != admiralty["id"]:
            errors.append(
                f"Template practiceAreaId is '{template.get('practiceAreaId')}', "
                f"expected '{admiralty['id']}'."
            )
        if template.get("billingMethod") != "hourly":
            errors.append(
                f"Template billingMethod is '{template.get('billingMethod')}', expected 'hourly'."
            )

    # 3. Check new matter under Admiralty Law for Pacific Rim
    matter = next(
        (m for m in state.get("matters", [])
         if m.get("practiceAreaId") == admiralty["id"]
         and "pacific rim" in (
             next((c.get("displayName", "") for c in state.get("contacts", [])
                   if c["id"] == m.get("clientId")), "")
         ).lower()),
        None,
    )
    if matter is None:
        # Fallback: search by description
        matter = next(
            (m for m in state.get("matters", [])
             if m.get("practiceAreaId") == admiralty["id"]),
            None,
        )

    if matter is None:
        errors.append("No matter found under Admiralty Law practice area.")
    else:
        # Check client is Pacific Rim (contact_10)
        if matter.get("clientId") != "contact_10":
            client = next(
                (c for c in state.get("contacts", []) if c["id"] == matter.get("clientId")),
                None,
            )
            client_name = client.get("displayName", "unknown") if client else "unknown"
            if "pacific rim" not in client_name.lower():
                errors.append(
                    f"Matter client is '{client_name}', expected Pacific Rim Imports & Exports."
                )

        # Check responsible attorney is William Park (user_16)
        if matter.get("responsibleAttorneyId") != "user_16":
            errors.append(
                f"Responsible attorney is '{matter.get('responsibleAttorneyId')}', "
                f"expected 'user_16' (William Park)."
            )

        # Check budget
        budget = matter.get("billing", {}).get("budget", 0)
        if abs(budget - 60000) > 5000:
            errors.append(f"Budget is ${budget:,.0f}, expected $60,000.")

    if errors:
        return False, "Admiralty Law setup not complete. " + " | ".join(errors)

    return True, (
        "Admiralty Law practice area created with correct stages, "
        "Admiralty - Cargo Dispute template created, and new matter created "
        "for Pacific Rim with William Park and $60,000 budget."
    )
