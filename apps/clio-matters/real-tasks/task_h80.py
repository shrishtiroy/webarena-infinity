import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    okafor = next(
        (m for m in state.get("matters", [])
         if "Okafor" in (m.get("description") or "") and "DUI" in (m.get("description") or "")),
        None,
    )
    if not okafor:
        return False, "Okafor DUI defense matter not found."

    state_farm = next(
        (c for c in state.get("contacts", [])
         if "State Farm" in (c.get("lastName") or "")),
        None,
    )
    riverside = next(
        (c for c in state.get("contacts", [])
         if "Riverside" in (c.get("lastName") or "")),
        None,
    )
    chen = next(
        (u for u in state.get("firmUsers", [])
         if u.get("fullName") == "James Chen"),
        None,
    )
    if not state_farm or not riverside or not chen:
        return False, "Required contacts or users not found."

    errors = []

    # Check recovery
    recovery = next(
        (r for r in okafor.get("settlement", {}).get("recoveries", [])
         if r.get("sourceContactId") == state_farm["id"] and r.get("amount") == 35000),
        None,
    )
    if not recovery:
        errors.append("No $35,000 recovery from State Farm Insurance found.")
    else:
        # Check legal fee
        fee = next(
            (f for f in okafor.get("settlement", {}).get("legalFees", [])
             if f.get("recoveryId") == recovery["id"]),
            None,
        )
        if not fee:
            errors.append("No legal fee found for the State Farm recovery.")
        else:
            if fee.get("recipientId") != chen["id"]:
                errors.append(
                    f"Legal fee recipient is '{fee.get('recipientId')}', "
                    f"expected '{chen['id']}' (James Chen)."
                )
            if fee.get("rate") != 25:
                errors.append(f"Legal fee rate is {fee.get('rate')}%, expected 25%.")

    # Check lien
    lien = next(
        (l for l in okafor.get("settlement", {}).get("otherLiens", [])
         if l.get("lienHolderId") == riverside["id"]
         and l.get("amount") == 3000),
        None,
    )
    if not lien:
        errors.append("No $3,000 lien from Riverside CU found.")
    elif "personal loan" not in (lien.get("description") or "").lower():
        errors.append(
            f"Lien description is '{lien.get('description')}', "
            f"expected to contain 'personal loan'."
        )

    if errors:
        return False, " ".join(errors)

    return True, "Okafor: State Farm recovery + Chen legal fee at 25% + Riverside CU lien."
