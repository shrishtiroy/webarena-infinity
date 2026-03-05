import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])
    apps = state.get("apps", [])
    errors = []

    # All open LCP-related recommendations should be resolved
    lcp_rec_titles = [
        "Reduce the impact of third-party scripts",
        "Optimize large hero images on homepage",
        "Evaluate Privy pop-up timing",
        "Enable pagination for large collections",
        "Reduce homepage sections",
    ]
    for title in lcp_rec_titles:
        rec = next((r for r in recommendations if r.get("title") == title), None)
        if rec is None:
            errors.append(f"Could not find recommendation '{title}'.")
        elif rec.get("status") != "resolved":
            errors.append(f"Recommendation '{title}' status is '{rec.get('status')}', expected 'resolved'.")

    # Apps with estimatedLcpImpact > 300 should be disabled
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

    if errors:
        return False, " ".join(errors)

    return True, "All 5 open LCP recommendations resolved and all 4 high-LCP-impact apps disabled."
