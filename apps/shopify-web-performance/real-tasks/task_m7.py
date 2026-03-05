import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])

    high_priority_titles = [
        "Reduce the impact of third-party scripts",
        "Optimize large hero images on homepage",
        "Reserve space for Privy pop-up banner",
    ]

    errors = []
    for title in high_priority_titles:
        found = None
        for rec in recommendations:
            if rec.get("title") == title:
                found = rec
                break
        if found is None:
            errors.append(f"Recommendation '{title}' not found in recommendations list.")
            continue
        if found.get("status") != "resolved":
            errors.append(f"Recommendation '{title}' status is '{found.get('status')}', expected 'resolved'.")

    if errors:
        return False, " ".join(errors)

    return True, "All high-priority recommendations are marked as resolved."
