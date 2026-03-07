import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matter = next((m for m in state["matters"] if "Rodriguez v. Premier Auto" in m["description"]), None)
    if not matter:
        return False, "Matter 'Rodriguez v. Premier Auto' not found."

    damages = matter.get("damages", [])
    match = next(
        (d for d in damages if d.get("description") == "Vehicle repair costs"),
        None
    )
    if match:
        return False, (
            f"Damage 'Vehicle repair costs' still exists (amount: {match.get('amount')}). It should have been removed."
        )

    return True, "Damage 'Vehicle repair costs' has been successfully removed."
