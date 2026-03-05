import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    apps = state.get("apps", [])
    tags = state.get("tagManagerTags", [])
    errors = []

    # Dawn should be published
    dawn = next((t for t in themes if "Dawn" in t.get("name", "")), None)
    if dawn is None:
        errors.append("Could not find Dawn theme in themes list.")
    else:
        if dawn.get("role") != "main":
            errors.append(f"Dawn role is '{dawn.get('role')}', expected 'main'.")
        if dawn.get("status") != "published":
            errors.append(f"Dawn status is '{dawn.get('status')}', expected 'published'.")

    # Horizon should be unpublished
    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        errors.append("Could not find theme 'Horizon - Outdoors' in themes list.")
    else:
        if horizon.get("role") != "unpublished":
            errors.append(f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'.")

    # Apps with >2 scripts should be disabled
    multi_script_substrings = ["Klaviyo", "Recharge Subscriptions", "Privy"]
    for substring in multi_script_substrings:
        app = next((a for a in apps if substring in a.get("name", "")), None)
        if app is None:
            errors.append(f"Could not find app containing '{substring}' in apps list.")
            continue
        if app.get("status") != "disabled":
            errors.append(f"App '{app.get('name')}' status is '{app.get('status')}', expected 'disabled'.")
        if app.get("loadsOnStorefront") is not False:
            errors.append(f"App '{app.get('name')}' loadsOnStorefront is {app.get('loadsOnStorefront')}, expected False.")

    # Google Ads Conversion tag should be removed
    gads_tag = next((t for t in tags if t.get("name") == "Google Ads Conversion"), None)
    if gads_tag is not None:
        errors.append("Tag 'Google Ads Conversion' should have been removed but still exists.")

    if errors:
        return False, " ".join(errors)

    return True, "Dawn published, Horizon unpublished, multi-script apps disabled, Google Ads Conversion tag removed."
