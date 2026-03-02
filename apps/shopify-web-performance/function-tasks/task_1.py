import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    target = None
    for app in apps:
        if app.get("name") == "Klaviyo: Email Marketing & SMS":
            target = app
            break

    if target is None:
        return False, "App 'Klaviyo: Email Marketing & SMS' not found in state."

    if target.get("status") != "disabled":
        return False, f"App status is '{target.get('status')}', expected 'disabled'."

    if target.get("loadsOnStorefront") is not False:
        return False, f"App loadsOnStorefront is {target.get('loadsOnStorefront')}, expected False."

    return True, "App 'Klaviyo: Email Marketing & SMS' is correctly disabled with loadsOnStorefront=False."
