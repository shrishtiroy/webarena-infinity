import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Northwestern Memorial Hospital contact
    contacts = state.get("contacts", [])
    nw_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Northwestern Memorial Hospital"),
        None
    )
    if not nw_contact:
        return False, "Contact 'Northwestern Memorial Hospital' (company) not found in contacts."

    nw_id = nw_contact["id"]
    other_liens = matter.get("settlement", {}).get("otherLiens", [])
    match = next(
        (ol for ol in other_liens
         if ol.get("lienHolderId") == nw_id
         and ol.get("description") == "Hospital treatment lien"
         and ol.get("amount") == 12000),
        None
    )
    if not match:
        nw_liens = [ol for ol in other_liens if ol.get("lienHolderId") == nw_id]
        if nw_liens:
            return False, (
                f"Found lien(s) from Northwestern Memorial Hospital but none match expected values. "
                f"Found: {nw_liens}"
            )
        return False, "No lien found from Northwestern Memorial Hospital."

    return True, (
        "Lien from Northwestern Memorial Hospital with description 'Hospital treatment lien' "
        "and amount 12000 found."
    )
