import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    target = None
    for app in apps:
        if "Privy" in app.get("name", ""):
            target = app
            break

    if target is None:
        return False, "No app with 'Privy' in its name found in state."

    if target.get("status") != "disabled":
        return False, f"App '{target.get('name')}' status is '{target.get('status')}', expected 'disabled'."

    if target.get("loadsOnStorefront") is not False:
        return False, f"App '{target.get('name')}' loadsOnStorefront is {target.get('loadsOnStorefront')}, expected False."

    return True, f"App '{target.get('name')}' is correctly disabled with loadsOnStorefront=False."
