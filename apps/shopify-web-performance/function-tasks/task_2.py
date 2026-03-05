import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    target = None
    for app in apps:
        if app.get("name") == "SEO Manager":
            target = app
            break

    if target is None:
        return False, "App 'SEO Manager' not found in state."

    if target.get("status") != "active":
        return False, f"App status is '{target.get('status')}', expected 'active'."

    if target.get("loadsOnStorefront") is not False:
        return False, f"App loadsOnStorefront is {target.get('loadsOnStorefront')}, expected False (scriptsCount=0)."

    return True, "App 'SEO Manager' is correctly enabled with status='active' and loadsOnStorefront=False."
