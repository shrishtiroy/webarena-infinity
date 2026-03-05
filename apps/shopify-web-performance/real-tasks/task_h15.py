import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    recommendations = state.get("recommendations", [])
    errors = []

    # Disabled apps should be removed
    disabled_app_names = ["SEO Manager", "Infinite Options"]
    for app_name in disabled_app_names:
        found = next((a for a in apps if a.get("name") == app_name), None)
        if found is not None:
            errors.append(f"Disabled app '{app_name}' should have been removed but still exists.")

    # Low-priority open recs should be dismissed
    low_priority_open_rec_titles = [
        "Enable pagination for large collections",
        "Preload web fonts",
    ]
    for title in low_priority_open_rec_titles:
        rec = next((r for r in recommendations if r.get("title") == title), None)
        if rec is None:
            errors.append(f"Could not find recommendation '{title}'.")
        elif rec.get("status") != "dismissed":
            errors.append(f"Recommendation '{title}' status is '{rec.get('status')}', expected 'dismissed'.")

    if errors:
        return False, " ".join(errors)

    return True, "All disabled apps removed and low-priority open recommendations dismissed."
