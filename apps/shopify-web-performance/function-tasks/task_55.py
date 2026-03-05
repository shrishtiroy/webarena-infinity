import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check Klaviyo app is disabled
    apps = state.get("apps", [])
    klaviyo = None
    for app in apps:
        if app.get("name") == "Klaviyo: Email Marketing & SMS":
            klaviyo = app
            break

    if klaviyo is None:
        errors.append("App 'Klaviyo: Email Marketing & SMS' not found in state.")
    else:
        if klaviyo.get("status") != "disabled":
            errors.append(f"Klaviyo app status is '{klaviyo.get('status')}', expected 'disabled'.")
        if klaviyo.get("loadsOnStorefront") is not False:
            errors.append(f"Klaviyo app loadsOnStorefront is {klaviyo.get('loadsOnStorefront')}, expected False.")

    # Check Meta Pixel tag is removed
    tags = state.get("tagManagerTags", [])
    for tag in tags:
        if tag.get("name") == "Meta Pixel":
            errors.append("Tag 'Meta Pixel' still exists in state. It should have been removed.")
            break

    if errors:
        return False, " ".join(errors)

    return True, "Klaviyo app is correctly disabled and Meta Pixel tag has been successfully removed."
