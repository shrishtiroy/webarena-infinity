import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify default pharmacy set to Express Scripts Mail Pharmacy."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    settings = state.get("settings", {})
    errors = []

    default_pharm = settings.get("defaultPharmacyId")
    if default_pharm != "pharm_011":
        # Also check by name in case the pharmacy list has the right one
        pharmacies = state.get("pharmacies", [])
        pharm_name = None
        for p in pharmacies:
            if p.get("id") == default_pharm:
                pharm_name = p.get("name")
                break
        errors.append(
            f"Default pharmacy is '{default_pharm}' ({pharm_name}), "
            f"expected 'pharm_011' (Express Scripts Mail Pharmacy)"
        )

    if errors:
        return False, "Failures: " + "; ".join(errors)

    return True, "Default pharmacy set to Express Scripts Mail Pharmacy successfully."
