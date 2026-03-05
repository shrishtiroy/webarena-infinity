import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    app = next((a for a in apps if a.get("name") == "Klaviyo: Email Marketing & SMS"), None)
    if app is None:
        return False, "App 'Klaviyo: Email Marketing & SMS' not found in apps list."

    if app.get("status") != "disabled":
        return False, f"Expected Klaviyo app status to be 'disabled', but got '{app.get('status')}'."

    if app.get("loadsOnStorefront") is not False:
        return False, f"Expected Klaviyo app loadsOnStorefront to be False, but got '{app.get('loadsOnStorefront')}'."

    return True, "Klaviyo: Email Marketing & SMS app has been turned off (status=disabled, loadsOnStorefront=False)."
