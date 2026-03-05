import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    recommendations = state.get("recommendations", [])
    errors = []

    # Apps with estimatedLcpImpact > 300ms should be disabled
    high_lcp_substrings = ["Klaviyo", "Recharge Subscriptions", "Privy", "Hotjar"]
    for substring in high_lcp_substrings:
        app = next((a for a in apps if substring in a.get("name", "")), None)
        if app is None:
            errors.append(f"Could not find app containing '{substring}' in apps list.")
            continue
        if app.get("status") != "disabled":
            errors.append(f"App '{app.get('name')}' status is '{app.get('status')}', expected 'disabled'.")
        if app.get("loadsOnStorefront") is not False:
            errors.append(f"App '{app.get('name')}' loadsOnStorefront is {app.get('loadsOnStorefront')}, expected False.")

    # Third-party scripts recommendation should be resolved
    rec = next((r for r in recommendations if r.get("title") == "Reduce the impact of third-party scripts"), None)
    if rec is None:
        errors.append("Could not find recommendation 'Reduce the impact of third-party scripts'.")
    elif rec.get("status") != "resolved":
        errors.append(f"Recommendation 'Reduce the impact of third-party scripts' status is '{rec.get('status')}', expected 'resolved'.")

    if errors:
        return False, " ".join(errors)

    return True, "All apps with >300ms LCP impact disabled and third-party scripts recommendation resolved."
