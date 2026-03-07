import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Riverside Community Credit Union contact
    contacts = state.get("contacts", [])
    rccu_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Riverside Community Credit Union"),
        None
    )
    if not rccu_contact:
        return False, "Contact 'Riverside Community Credit Union' (company) not found in contacts."

    rccu_id = rccu_contact["id"]
    other_liens = matter.get("settlement", {}).get("otherLiens", [])
    match = next(
        (ol for ol in other_liens
         if ol.get("lienHolderId") == rccu_id
         and ol.get("reduction") == 1000),
        None
    )
    if not match:
        rccu_liens = [ol for ol in other_liens if ol.get("lienHolderId") == rccu_id]
        if rccu_liens:
            reductions = [ol.get("reduction") for ol in rccu_liens]
            return False, (
                f"Found lien(s) from Riverside Community Credit Union but reduction is "
                f"{reductions}, expected 1000."
            )
        return False, "No lien found from Riverside Community Credit Union."

    return True, "Lien from Riverside Community Credit Union with reduction 1000 found."
