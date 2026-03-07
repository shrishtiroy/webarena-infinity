import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Dr. Amanda Reeves"
    contact = next(
        (c for c in state["contacts"] if c.get("firstName") == "Dr. Amanda" and c.get("lastName") == "Reeves"),
        None
    )
    if not contact:
        return False, "Contact 'Dr. Amanda Reeves' not found."

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
        return False, "No medical provider with contactId for 'Dr. Amanda Reeves' found on matter 'Rodriguez v. Premier Auto'."

    record_status = provider.get("recordStatus")
    if record_status != "Received":
        return False, f"Provider 'Dr. Amanda Reeves' recordStatus is '{record_status}', expected 'Received'."

    return True, "Provider 'Dr. Amanda Reeves' on matter 'Rodriguez v. Premier Auto' has recordStatus 'Received'."
