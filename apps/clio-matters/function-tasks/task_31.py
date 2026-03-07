import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find contact "Chicago Physical Therapy Center"
    contact = next((c for c in state["contacts"] if c["lastName"] == "Chicago Physical Therapy Center"), None)
    if not contact:
        return False, "Contact 'Chicago Physical Therapy Center' not found."

    # Find matter "Harris v. ABC Construction"
    matter = next((m for m in state["matters"] if "Harris" in m["description"] and "ABC Construction" in m["description"]), None)
    if not matter:
        return False, "Matter 'Harris v. ABC Construction' not found."

    # Find provider with matching contactId and description
    provider = next(
        (p for p in matter.get("medicalProviders", [])
         if p["contactId"] == contact["id"] and p.get("description") == "Post-surgical hand rehabilitation"),
        None
    )
    if not provider:
        return False, (
            f"No medical provider with contactId for 'Chicago Physical Therapy Center' and "
            f"description 'Post-surgical hand rehabilitation' found on matter 'Harris v. ABC Construction'. "
            f"Providers: {[{{'contactId': p['contactId'], 'description': p.get('description')}} for p in matter.get('medicalProviders', [])]}"
        )

    return True, "Matter 'Harris v. ABC Construction' has a medical provider for 'Chicago Physical Therapy Center' with description 'Post-surgical hand rehabilitation'."
