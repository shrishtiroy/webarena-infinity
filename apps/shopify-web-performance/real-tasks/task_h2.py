import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    errors = []

    removed_substrings = ["Recharge Subscriptions", "Privy", "Hotjar"]
    for substring in removed_substrings:
        found = next((a for a in apps if substring in a.get("name", "")), None)
        if found is not None:
            errors.append(f"App '{found.get('name')}' should have been removed but still exists in the apps list.")

    if errors:
        return False, " ".join(errors)

    return True, "All non-Shopify high-impact apps (Recharge Subscriptions, Privy, Hotjar) have been removed."
