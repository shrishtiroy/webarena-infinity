import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    app = next((a for a in apps if a.get("name") == "Recharge Subscriptions"), None)
    if app is None:
        return False, "App 'Recharge Subscriptions' not found in apps list."

    if app.get("status") != "disabled":
        return False, f"Expected Recharge Subscriptions app status to be 'disabled', but got '{app.get('status')}'."

    if app.get("loadsOnStorefront") is not False:
        return False, f"Expected Recharge Subscriptions app loadsOnStorefront to be False, but got '{app.get('loadsOnStorefront')}'."

    return True, "Recharge Subscriptions app has been disabled (status=disabled, loadsOnStorefront=False)."
