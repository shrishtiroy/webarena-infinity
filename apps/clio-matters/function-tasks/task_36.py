import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Northwestern Memorial Hospital"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Northwestern Memorial Hospital"), None)
    if not contact:
        return False, "Contact 'Northwestern Memorial Hospital' not found."

    # Find matter "Rodriguez v. Premier Auto"
    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find provider
    provider = next(
        (p for p in matter.get("medicalProviders", []) if p["contactId"] == contact["id"]),
        None
    )
    if not provider:
        return False, "No medical provider with contactId for 'Northwestern Memorial Hospital' found on matter 'Rodriguez v. Premier Auto'."

    # Find medical record with fileName "Post_Op_Follow_Up.pdf"
    record = next(
        (r for r in provider.get("medicalRecords", []) if r.get("fileName") == "Post_Op_Follow_Up.pdf"),
        None
    )
    if not record:
        existing = [r.get("fileName") for r in provider.get("medicalRecords", [])]
        return False, f"No medical record with fileName 'Post_Op_Follow_Up.pdf' found. Existing records: {existing}"

    received_date = record.get("receivedDate")
    if received_date != "2026-01-10":
        return False, f"Medical record 'Post_Op_Follow_Up.pdf' has receivedDate '{received_date}', expected '2026-01-10'."

    return True, "Provider 'Northwestern Memorial Hospital' on matter 'Rodriguez v. Premier Auto' has medical record 'Post_Op_Follow_Up.pdf' with receivedDate '2026-01-10'."
