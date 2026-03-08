import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    firm_users = state.get("firmUsers", [])
    partners = [u for u in firm_users if u.get("role") == "Partner"]
    if len(partners) < 2:
        return False, f"Expected at least 2 partners, found {len(partners)}."

    partners_sorted = sorted(partners, key=lambda u: u.get("rate", 0))
    less_expensive = partners_sorted[0]
    more_expensive = partners_sorted[-1]

    mendez = None
    for m in state.get("matters", []):
        if "Mendez" in (m.get("description") or ""):
            mendez = m
            break
    if not mendez:
        return False, "Mendez work visa matter not found."

    errors = []
    if mendez.get("responsibleAttorneyId") != less_expensive["id"]:
        errors.append(
            f"Responsible attorney is '{mendez.get('responsibleAttorneyId')}', "
            f"expected '{less_expensive['id']}' ({less_expensive['fullName']}, "
            f"${less_expensive['rate']}/hr)."
        )
    if mendez.get("originatingAttorneyId") != more_expensive["id"]:
        errors.append(
            f"Originating attorney is '{mendez.get('originatingAttorneyId')}', "
            f"expected '{more_expensive['id']}' ({more_expensive['fullName']}, "
            f"${more_expensive['rate']}/hr)."
        )

    if errors:
        return False, " ".join(errors)

    return True, (
        f"Mendez attorneys set: responsible={less_expensive['fullName']}, "
        f"originating={more_expensive['fullName']}."
    )
