import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    app = next((a for a in apps if a.get("name") == "SEO Manager"), None)
    if app is None:
        return False, "App 'SEO Manager' not found in apps list."

    if app.get("status") != "active":
        return False, f"Expected SEO Manager app status to be 'active', but got '{app.get('status')}'."

    return True, "SEO Manager app has been re-enabled (status=active)."
