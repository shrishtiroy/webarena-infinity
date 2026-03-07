import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Advanced Imaging Associates"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Advanced Imaging Associates"), None)
    if not contact:
        return False, "Contact 'Advanced Imaging Associates' not found."

    # Find matter "Rodriguez v. Premier Auto"
    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Check that NO provider has this contactId
    provider = next(
        (p for p in matter.get("medicalProviders", []) if p["contactId"] == contact["id"]),
        None
    )
    if provider is not None:
        return False, (
            f"Matter 'Rodriguez v. Premier Auto' still has a medical provider with contactId for "
            f"'Advanced Imaging Associates' (provider id: {provider.get('id')})."
        )

    return True, "Matter 'Rodriguez v. Premier Auto' does not have a medical provider for 'Advanced Imaging Associates'."
