import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00001" or "Patterson" in m.get("displayNumber", ""):
            matter = m
            break

    if matter is None:
        return False, "Could not find matter '00001-Patterson'."

    relationships = matter.get("relationships", [])
    found = False
    for rel in relationships:
        if rel.get("contactId") == "contact_45" and rel.get("relationship") == "Parent":
            found = True
            break

    if not found:
        current_rels = [
            f"contactId={r.get('contactId')}, relationship={r.get('relationship')}"
            for r in relationships
        ]
        return False, f"Expected a relationship with contactId 'contact_45' (Linda Patterson) and relationship 'Parent' in matter '00001-Patterson'. Current relationships: [{'; '.join(current_rels)}]."

    return True, "Matter '00001-Patterson' has a relationship with contact_45 (Linda Patterson) with type 'Parent'."
