import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    errors = []
    updated_count = 0
    for p in rodriguez.get("medicalProviders", []):
        contact_id = p.get("contactId")
        contact = next(
            (c for c in state.get("contacts", []) if c["id"] == contact_id),
            None,
        )
        name = (contact.get("lastName") or contact.get("firstName", "")) if contact else contact_id

        # Dr. Reeves was the only provider with billStatus="Not yet requested" in seed
        if "Reeves" in str(name) or "Amanda" in str(name):
            if p.get("billStatus") != "Requested":
                errors.append(
                    f"Dr. Reeves bill status is '{p.get('billStatus')}', expected 'Requested'."
                )
            elif p.get("billRequestDate") != "2026-03-05":
                errors.append(
                    f"Dr. Reeves bill request date is '{p.get('billRequestDate')}', "
                    f"expected '2026-03-05'."
                )
            else:
                updated_count += 1

    if updated_count == 0 and not errors:
        errors.append("No providers were updated to 'Requested' status.")

    if errors:
        return False, " ".join(errors)

    return True, "Bill request status set to 'Requested' with date 2026-03-05 for applicable providers."
