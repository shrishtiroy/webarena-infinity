import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    recommendations = state.get("recommendations", [])
    errors = []

    # All marketing category apps should be disabled
    marketing_apps = [
        "Klaviyo: Email Marketing & SMS",
        "Privy ‑ Pop Ups, Email, & SMS",
        "Back in Stock Alerts",
    ]
    for app_name in marketing_apps:
        app = next((a for a in apps if a.get("name") == app_name), None)
        if app is None:
            errors.append(f"Could not find app '{app_name}' in apps list.")
            continue
        if app.get("status") != "disabled":
            errors.append(f"App '{app_name}' status is '{app.get('status')}', expected 'disabled'.")
        if app.get("loadsOnStorefront") is not False:
            errors.append(f"App '{app_name}' loadsOnStorefront is {app.get('loadsOnStorefront')}, expected False.")

    # Both Privy-related recommendations should be resolved
    privy_rec_titles = [
        "Evaluate Privy pop-up timing",
        "Reserve space for Privy pop-up banner",
    ]
    for title in privy_rec_titles:
        rec = next((r for r in recommendations if r.get("title") == title), None)
        if rec is None:
            errors.append(f"Could not find recommendation '{title}'.")
        elif rec.get("status") != "resolved":
            errors.append(f"Recommendation '{title}' status is '{rec.get('status')}', expected 'resolved'.")

    if errors:
        return False, " ".join(errors)

    return True, "All marketing apps disabled with loadsOnStorefront=False and both Privy recommendations resolved."
