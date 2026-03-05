import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    errors = []

    removed_substrings = ["Klaviyo", "Recharge Subscriptions", "Privy"]
    for substring in removed_substrings:
        found = next((a for a in apps if substring in a.get("name", "")), None)
        if found is not None:
            errors.append(f"App '{found.get('name')}' has more than 2 scripts and should have been removed but still exists.")

    if errors:
        return False, " ".join(errors)

    return True, "All apps with more than 2 scripts (Klaviyo, Recharge Subscriptions, Privy) have been removed."
