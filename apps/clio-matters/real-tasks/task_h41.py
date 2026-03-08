import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    firm_users = state.get("firmUsers", [])
    partners = [u for u in firm_users if u.get("role") == "Partner"]
    if not partners:
        return False, "No partners found."
    highest_partner = max(partners, key=lambda u: u.get("rate", 0))

    associates = [u for u in firm_users if u.get("role") == "Associate"]
    if not associates:
        return False, "No associates found."
    highest_associate = max(associates, key=lambda u: u.get("rate", 0))

    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez auto accident matter not found."

    errors = []
    if rodriguez.get("responsibleAttorneyId") != highest_partner["id"]:
        errors.append(
            f"Responsible attorney is '{rodriguez.get('responsibleAttorneyId')}', "
            f"expected '{highest_partner['id']}' ({highest_partner['fullName']})."
        )
    if rodriguez.get("originatingAttorneyId") != highest_associate["id"]:
        errors.append(
            f"Originating attorney is '{rodriguez.get('originatingAttorneyId')}', "
            f"expected '{highest_associate['id']}' ({highest_associate['fullName']})."
        )

    if errors:
        return False, " ".join(errors)

    return True, (
        f"Rodriguez attorneys updated: responsible={highest_partner['fullName']}, "
        f"originating={highest_associate['fullName']}."
    )
