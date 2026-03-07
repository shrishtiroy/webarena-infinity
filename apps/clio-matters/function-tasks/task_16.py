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
        (d for d in damages
         if d.get("description") == "Prescription medication costs"
         and d.get("type") == "Out-of-Pocket Expenses"
         and d.get("category") == "Special"
         and d.get("amount") == 2500),
        None
    )
    if not match:
        descs = [d.get("description") for d in damages]
        return False, (
            f"No damage found with description 'Prescription medication costs', "
            f"type 'Out-of-Pocket Expenses', category 'Special', amount 2500. "
            f"Current damage descriptions: {descs}"
        )

    return True, "Damage 'Prescription medication costs' with correct type, category, and amount found."
