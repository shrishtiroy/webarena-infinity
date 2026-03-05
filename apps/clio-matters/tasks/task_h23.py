import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Okafor burn injury matter
    matter = next(
        (m for m in state.get("matters", [])
         if "okafor" in m.get("description", "").lower()
         and "burn" in m.get("description", "").lower()),
        None
    )
    if matter is None:
        return False, "Could not find Okafor burn injury matter."

    matter_id = matter["id"]

    # Check matter stage is Settlement/Trial (stage_1_5)
    if matter.get("stageId") != "stage_1_5":
        errors.append(
            f"Okafor burn matter stageId is '{matter.get('stageId')}', "
            f"expected 'stage_1_5' (Settlement/Trial)."
        )

    # Check all medical providers for this matter have treatmentComplete = true
    providers = [
        mp for mp in state.get("medicalProviders", [])
        if mp.get("matterId") == matter_id
    ]

    if not providers:
        errors.append(f"No medical providers found for matter {matter_id}.")
    else:
        incomplete = [
            mp for mp in providers
            if not mp.get("treatmentComplete")
        ]
        if incomplete:
            incomplete_ids = [mp.get("id") for mp in incomplete]
            errors.append(
                f"{len(incomplete)} medical provider(s) still not marked as treatment complete: "
                f"{incomplete_ids}."
            )

    if errors:
        return False, "Okafor burn case not updated correctly. " + " | ".join(errors)

    return True, (
        f"Okafor burn matter ({matter_id}) moved to Settlement/Trial and all "
        f"{len(providers)} medical providers marked as treatment complete."
    )
