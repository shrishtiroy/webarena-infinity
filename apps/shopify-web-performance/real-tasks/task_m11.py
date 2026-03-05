import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    app_names = [app.get("name", "") for app in apps]

    still_present = []
    for target in ["SEO Manager", "Infinite Options"]:
        if target in app_names:
            still_present.append(target)

    if still_present:
        return False, f"The following apps are still present in the apps list: {', '.join(still_present)}."

    return True, "Both SEO Manager and Infinite Options apps have been removed from the apps list."
