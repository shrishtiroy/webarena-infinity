import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    # Find Lakeside Insurance Co. contact
    contacts = state.get("contacts", [])
    lakeside_contact = next(
        (c for c in contacts
         if c.get("type") == "company" and c.get("lastName") == "Lakeside Insurance Co."),
        None
    )
    if not lakeside_contact:
        return False, "Contact 'Lakeside Insurance Co.' (company) not found in contacts."

    # Find Michael Osei in firmUsers
    firm_users = state.get("firmUsers", [])
    osei_user = next(
        (u for u in firm_users if u.get("fullName") == "Michael Osei"),
        None
    )
    if not osei_user:
        return False, "Firm user 'Michael Osei' not found."

    osei_id = osei_user["id"]
    lakeside_id = lakeside_contact["id"]

    # Find recoveries from Lakeside Insurance Co.
    recoveries = matter.get("settlement", {}).get("recoveries", [])
    lakeside_recovery_ids = {r["id"] for r in recoveries if r.get("sourceContactId") == lakeside_id}
    if not lakeside_recovery_ids:
        return False, "No recovery found from Lakeside Insurance Co."

    # Check legal fees
    legal_fees = matter.get("settlement", {}).get("legalFees", [])
    match = next(
        (lf for lf in legal_fees
         if lf.get("recipientId") == osei_id
         and lf.get("rate") == 25
         and lf.get("recoveryId") in lakeside_recovery_ids),
        None
    )
    if not match:
        relevant_fees = [lf for lf in legal_fees if lf.get("recoveryId") in lakeside_recovery_ids]
        return False, (
            f"No legal fee found with recipientId matching Michael Osei, rate 25, "
            f"and recoveryId referencing Lakeside Insurance Co. "
            f"Legal fees for Lakeside recoveries: {relevant_fees}"
        )

    return True, (
        "Legal fee found with recipient Michael Osei, rate 25, referencing "
        "Lakeside Insurance Co. recovery."
    )
