import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find McCarthy pedestrian case
    matter = next(
        (m for m in state.get("matters", [])
         if "mccarthy" in m.get("description", "").lower()
         and ("pedestrian" in m.get("description", "").lower()
              or "san francisco" in m.get("description", "").lower()
              or "crosswalk" in m.get("description", "").lower())),
        None,
    )
    if matter is None:
        return False, "McCarthy pedestrian case not found."

    matter_id = matter["id"]
    providers = state.get("medicalProviders", [])
    matter_providers = [p for p in providers if p.get("matterId") == matter_id]

    # Old providers (mp_11 Bay Area Orthopedic, mp_12 Dr. Reeves) should be gone
    old_provider_ids = {"mp_11", "mp_12"}
    remaining_old = [p for p in matter_providers if p["id"] in old_provider_ids]
    if remaining_old:
        errors.append(
            f"Old providers still exist: {[p['id'] for p in remaining_old]}. "
            f"Expected them to be deleted."
        )

    # Should have UCSF Medical Center (contact_59) as provider
    has_ucsf = any(
        p.get("contactId") == "contact_59"
        or "ucsf" in p.get("description", "").lower()
        for p in matter_providers
    )
    if not has_ucsf:
        errors.append("UCSF Medical Center not found as provider on McCarthy case.")

    # Should have Horizon Healthcare Partners (contact_68) as provider
    has_horizon = any(
        p.get("contactId") == "contact_68"
        or "horizon" in p.get("description", "").lower()
        for p in matter_providers
    )
    if not has_horizon:
        errors.append("Horizon Healthcare Partners not found as provider on McCarthy case.")

    # Old records and bills for mp_11/mp_12 should be gone
    old_records = [
        r for r in state.get("medicalRecords", [])
        if r.get("providerId") in old_provider_ids and r.get("matterId") == matter_id
    ]
    if old_records:
        errors.append(
            f"{len(old_records)} old medical records still reference deleted providers."
        )

    old_bills = [
        b for b in state.get("medicalBills", [])
        if b.get("providerId") in old_provider_ids and b.get("matterId") == matter_id
    ]
    if old_bills:
        errors.append(
            f"{len(old_bills)} old medical bills still reference deleted providers."
        )

    if errors:
        return False, (
            "McCarthy case provider replacement not correct. " + " | ".join(errors)
        )

    return True, (
        "McCarthy pedestrian case providers correctly replaced: "
        "old providers deleted, UCSF Medical Center and Horizon Healthcare Partners added."
    )
