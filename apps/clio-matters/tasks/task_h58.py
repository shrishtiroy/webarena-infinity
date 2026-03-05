import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the new Dimitriou matter (not the existing ones)
    dimitriou_matters = [
        m for m in state.get("matters", [])
        if "dimitriou" in m.get("description", "").lower()
        and ("oakland" in m.get("description", "").lower()
             or "sidewalk" in m.get("description", "").lower())
    ]

    if not dimitriou_matters:
        return False, "Could not find the new Dimitriou v. City of Oakland matter."

    matter = dimitriou_matters[0]
    matter_id = matter["id"]

    # Check client is Angela Dimitriou (contact_53)
    if matter.get("clientId") != "contact_53":
        # Try to verify by contact name
        contact = next(
            (c for c in state.get("contacts", [])
             if c["id"] == matter.get("clientId")
             and "dimitriou" in c.get("displayName", "").lower()),
            None
        )
        if contact is None:
            errors.append(
                f"Client is '{matter.get('clientId')}', expected Angela Dimitriou (contact_53)."
            )

    # Check responsible attorney is Diana Reyes (user_3)
    if matter.get("responsibleAttorneyId") != "user_3":
        errors.append(
            f"Responsible attorney is '{matter.get('responsibleAttorneyId')}', "
            f"expected 'user_3' (Diana Reyes)."
        )

    # Check practice area is PI (pa_1)
    if matter.get("practiceAreaId") != "pa_1":
        errors.append(
            f"Practice area is '{matter.get('practiceAreaId')}', expected 'pa_1' (Personal Injury)."
        )

    # Check billing is contingency at ~33.33%
    billing = matter.get("billing", {})
    method = matter.get("billingMethod", billing.get("method"))
    if method != "contingency":
        errors.append(f"Billing method is '{method}', expected 'contingency'.")
    else:
        cont_fee = billing.get("contingencyFee", {})
        if cont_fee:
            pct = float(cont_fee.get("percentage", 0))
            if abs(pct - 33.33) < 5:
                pass  # OK
            else:
                errors.append(f"Contingency percentage is {pct}%, expected ~33.33%.")
        else:
            errors.append("No contingency fee configured.")

    # Check for document folder "Incident Photos"
    folders = matter.get("documentFolders", [])
    has_folder = any(
        "incident" in f.get("name", "").lower() and "photo" in f.get("name", "").lower()
        for f in folders
    )
    if not has_folder:
        folder_names = [f.get("name") for f in folders]
        errors.append(
            f"No 'Incident Photos' document folder found. Folders: {folder_names}."
        )

    if errors:
        return False, "New Dimitriou matter not created correctly. " + " | ".join(errors)

    return True, (
        f"New Dimitriou v. City of Oakland matter ({matter_id}) correctly created: "
        f"client Angela Dimitriou, attorney Diana Reyes, contingency at 33.33%, "
        f"Incident Photos folder added."
    )
