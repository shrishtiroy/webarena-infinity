import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Patterson bus accident matter (matter_1)
    matter = next(
        (m for m in state.get("matters", [])
         if "patterson" in m.get("description", "").lower()
         and ("bus" in m.get("description", "").lower()
              or "metro transit" in m.get("description", "").lower())),
        None
    )
    if matter is None:
        return False, "Could not find Patterson bus accident matter."

    matter_id = matter["id"]

    # Find the first listed medical provider for this matter
    # mp_1: SF General Hospital (contact_55)
    providers = [
        mp for mp in state.get("medicalProviders", [])
        if mp.get("matterId") == matter_id
    ]

    if not providers:
        return False, f"No medical providers found for Patterson bus accident ({matter_id})."

    first_provider = providers[0]

    # Check record status is 'certified'
    if first_provider.get("recordStatus") != "certified":
        errors.append(
            f"First provider ({first_provider.get('id')}) record status is "
            f"'{first_provider.get('recordStatus')}', expected 'certified'."
        )

    # Check bill status is 'received'
    if first_provider.get("billStatus") != "received":
        errors.append(
            f"First provider ({first_provider.get('id')}) bill status is "
            f"'{first_provider.get('billStatus')}', expected 'received'."
        )

    # Check for 'Settlement Documents' document folder on the matter
    doc_folders = matter.get("documentFolders", [])
    has_settlement_folder = any(
        "settlement" in f.get("name", "").lower()
        and "document" in f.get("name", "").lower()
        for f in doc_folders
    )
    if not has_settlement_folder:
        folder_names = [f.get("name") for f in doc_folders]
        errors.append(
            f"No 'Settlement Documents' folder found. Current folders: {folder_names}."
        )

    if errors:
        return False, "Patterson bus accident matter not updated correctly. " + " | ".join(errors)

    return True, (
        f"Patterson bus accident ({matter_id}): first provider record status=certified, "
        f"bill status=received, and 'Settlement Documents' folder added."
    )
