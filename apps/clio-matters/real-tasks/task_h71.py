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

    # In seed: 3 providers have recordStatus='Received' (NM Hospital, Chicago PT, AIA)
    # Dr. Reeves has recordStatus='Requested' and should NOT be updated
    errors = []
    received_count = 0
    for p in rodriguez.get("medicalProviders", []):
        contact = next(
            (c for c in state.get("contacts", []) if c["id"] == p.get("contactId")),
            None,
        )
        name = (contact.get("lastName") or "") if contact else p.get("contactId")

        if p.get("recordStatus") == "Received":
            if p.get("recordFollowUpDate") != "2026-03-15":
                errors.append(
                    f"Provider '{name}': follow-up date is '{p.get('recordFollowUpDate')}', "
                    f"expected '2026-03-15'."
                )
            else:
                received_count += 1

    if received_count < 3 and not errors:
        errors.append(f"Expected at least 3 providers with follow-up date set, found {received_count}.")

    if errors:
        return False, " ".join(errors)

    return True, "Follow-up date set to March 15, 2026 for all 'Received' status providers."
