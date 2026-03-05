import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    tags = state.get("tagManagerTags", [])
    errors = []

    hotjar_app = next((a for a in apps if "Hotjar" in a.get("name", "")), None)
    if hotjar_app is not None:
        errors.append(f"App '{hotjar_app.get('name')}' should have been removed but still exists.")

    hotjar_tag = next((t for t in tags if t.get("name") == "Hotjar Tracking"), None)
    if hotjar_tag is not None:
        errors.append("Tag 'Hotjar Tracking' should have been removed but still exists.")

    if errors:
        return False, " ".join(errors)

    return True, "Hotjar app and Hotjar Tracking tag have both been removed."
