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

    # Find medical record "ER_Admission_Report.pdf"
    record = next(
        (r for r in provider.get("medicalRecords", []) if r.get("fileName") == "ER_Admission_Report.pdf"),
        None
    )
    if not record:
        existing = [r.get("fileName") for r in provider.get("medicalRecords", [])]
        return False, f"No medical record with fileName 'ER_Admission_Report.pdf' found. Existing records: {existing}"

    # Check for comment with text "Critical evidence for demand package"
    target_text = "Critical evidence for demand package"
    comment = next(
        (c for c in record.get("comments", []) if c.get("text") == target_text),
        None
    )
    if not comment:
        existing_comments = [c.get("text") for c in record.get("comments", [])]
        return False, f"No comment with text '{target_text}' found on record 'ER_Admission_Report.pdf'. Existing comments: {existing_comments}"

    return True, f"Medical record 'ER_Admission_Report.pdf' on provider 'Northwestern Memorial Hospital' has comment '{target_text}'."
