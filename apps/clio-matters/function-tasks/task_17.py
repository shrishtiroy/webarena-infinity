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
         if d.get("description") == "Emergency Room Visit"
         and d.get("amount") == 18500),
        None
    )
    if not match:
        er_damages = [d for d in damages if d.get("description") == "Emergency Room Visit"]
        if er_damages:
            return False, (
                f"Found 'Emergency Room Visit' damage but amount is {er_damages[0].get('amount')}, expected 18500."
            )
        return False, "No damage found with description 'Emergency Room Visit'."

    return True, "Damage 'Emergency Room Visit' with amount 18500 found."
