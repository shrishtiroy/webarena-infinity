import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    tags = state.get("tagManagerTags", [])
    errors = []

    # TikTok and Meta apps should be disabled
    app_substrings = {"TikTok": None, "Meta Pixel": None}
    for substring in app_substrings:
        app = next((a for a in apps if substring in a.get("name", "")), None)
        if app is None:
            errors.append(f"Could not find app containing '{substring}' in apps list.")
            continue
        if app.get("status") != "disabled":
            errors.append(f"App '{app.get('name')}' status is '{app.get('status')}', expected 'disabled'.")
        if app.get("loadsOnStorefront") is not False:
            errors.append(f"App '{app.get('name')}' loadsOnStorefront is {app.get('loadsOnStorefront')}, expected False.")

    # TikTok Pixel and Meta Pixel tags should be deactivated
    tag_names = ["TikTok Pixel", "Meta Pixel"]
    for tag_name in tag_names:
        tag = next((t for t in tags if t.get("name") == tag_name), None)
        if tag is None:
            errors.append(f"Tag '{tag_name}' not found in tag manager tags list.")
        elif tag.get("status") != "inactive":
            errors.append(f"Tag '{tag_name}' status is '{tag.get('status')}', expected 'inactive'.")

    if errors:
        return False, " ".join(errors)

    return True, "TikTok and Meta apps disabled with loadsOnStorefront=False; TikTok Pixel and Meta Pixel tags deactivated."
