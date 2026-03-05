import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check that the Hotjar Tracking tag is inactive
    tags = state.get("tagManagerTags", [])
    hotjar_tag = None
    for tag in tags:
        if tag.get("name") == "Hotjar Tracking":
            hotjar_tag = tag
            break

    if hotjar_tag is None:
        errors.append("Tag 'Hotjar Tracking' not found in tagManagerTags list.")
    elif hotjar_tag.get("status") != "inactive":
        errors.append(f"Hotjar Tracking tag status is '{hotjar_tag.get('status')}', expected 'inactive'.")

    # Check that no app containing "Hotjar" exists
    apps = state.get("apps", [])
    hotjar_apps = [app.get("name") for app in apps if "Hotjar" in app.get("name", "")]
    if hotjar_apps:
        errors.append(f"Hotjar app(s) still present in apps list: {', '.join(hotjar_apps)}.")

    if errors:
        return False, " ".join(errors)

    return True, "Hotjar Tracking tag is deactivated and Hotjar app has been removed from the apps list."
