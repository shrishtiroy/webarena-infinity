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

    # Check that NO medical record has fileName "Surgical_Report_Lumbar.pdf"
    record = next(
        (r for r in provider.get("medicalRecords", []) if r.get("fileName") == "Surgical_Report_Lumbar.pdf"),
        None
    )
    if record is not None:
        return False, (
            f"Medical record 'Surgical_Report_Lumbar.pdf' still exists on provider 'Northwestern Memorial Hospital' "
            f"(record id: {record.get('id')})."
        )

    return True, "Provider 'Northwestern Memorial Hospital' on matter 'Rodriguez v. Premier Auto' does not have medical record 'Surgical_Report_Lumbar.pdf'."
