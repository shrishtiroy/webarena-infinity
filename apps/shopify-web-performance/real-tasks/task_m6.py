import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    analytics_app_names = [
        "Google Analytics (GA4)",
        "Meta Pixel & Conversions API",
        "Hotjar Heatmaps & Recordings",
    ]

    errors = []
    for target_name in analytics_app_names:
        found = None
        for app in apps:
            if app.get("name") == target_name:
                found = app
                break
        if found is None:
            # App was removed entirely; that also counts as disabled for our purposes,
            # but the task says "disable" not "remove", so we check it exists.
            errors.append(f"Analytics app '{target_name}' not found in apps list.")
            continue
        if found.get("status") != "disabled":
            errors.append(f"'{target_name}' status is '{found.get('status')}', expected 'disabled'.")
        if found.get("loadsOnStorefront") is not False:
            errors.append(f"'{target_name}' loadsOnStorefront is {found.get('loadsOnStorefront')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "All analytics category apps (Google Analytics GA4, Meta Pixel, Hotjar) are disabled with loadsOnStorefront set to False."
