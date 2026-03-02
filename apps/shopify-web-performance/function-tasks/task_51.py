import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])

    target_names = ["Recharge Subscriptions", "Privy", "Hotjar"]
    errors = []

    for target_name in target_names:
        found = None
        for app in apps:
            if target_name in app.get("name", ""):
                found = app
                break

        if found is None:
            errors.append(f"App containing '{target_name}' not found in state.")
            continue

        if found.get("status") != "disabled":
            errors.append(f"App '{found.get('name')}' status is '{found.get('status')}', expected 'disabled'.")

        if found.get("loadsOnStorefront") is not False:
            errors.append(f"App '{found.get('name')}' loadsOnStorefront is {found.get('loadsOnStorefront')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "All 3 high-impact apps (Recharge Subscriptions, Privy, Hotjar) are correctly disabled with loadsOnStorefront=False."
