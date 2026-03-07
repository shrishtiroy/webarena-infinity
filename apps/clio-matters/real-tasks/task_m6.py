import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Northwestern Memorial Hospital contact id
    contacts = state.get("contacts", [])
    nm_id = None
    for contact in contacts:
        name = contact.get("lastName", "") or ""
        if "Northwestern Memorial" in name:
            nm_id = contact.get("id", "")
            break
    if not nm_id:
        nm_id = "con_018"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Rodriguez" in desc or matter_id == "mat_001":
            providers = matter.get("medicalProviders", [])
            for provider in providers:
                if provider.get("contactId") == nm_id:
                    records = provider.get("medicalRecords", [])
                    for rec in records:
                        if rec.get("fileName") == "Post_Op_Evaluation.pdf":
                            received = rec.get("receivedDate", "") or ""
                            if "2026-01-10" in received:
                                return True, "Medical record Post_Op_Evaluation.pdf added to NM Hospital provider on Rodriguez with receivedDate 2026-01-10."
                            else:
                                return False, f"Found Post_Op_Evaluation.pdf but receivedDate is '{received}', expected to contain '2026-01-10'."
                    return False, "No medical record with fileName 'Post_Op_Evaluation.pdf' found in NM Hospital provider on Rodriguez."
            return False, "No medical provider with Northwestern Memorial Hospital contactId found on Rodriguez."

    return False, "Could not find the Rodriguez matter in state."
