import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])

    privy_app = None
    hotjar_app = None
    for app in apps:
        name = app.get("name", "")
        if "Privy" in name:
            privy_app = app
        if "Hotjar" in name:
            hotjar_app = app

    if privy_app is None:
        return False, "Could not find an app containing 'Privy' in the apps list."
    if hotjar_app is None:
        return False, "Could not find an app containing 'Hotjar' in the apps list."

    errors = []

    if privy_app.get("status") != "disabled":
        errors.append(f"Privy app status is '{privy_app.get('status')}', expected 'disabled'.")
    if privy_app.get("loadsOnStorefront") is not False:
        errors.append(f"Privy app loadsOnStorefront is {privy_app.get('loadsOnStorefront')}, expected False.")

    if hotjar_app.get("status") != "disabled":
        errors.append(f"Hotjar app status is '{hotjar_app.get('status')}', expected 'disabled'.")
    if hotjar_app.get("loadsOnStorefront") is not False:
        errors.append(f"Hotjar app loadsOnStorefront is {hotjar_app.get('loadsOnStorefront')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "Both Privy and Hotjar apps are disabled with loadsOnStorefront set to False."
