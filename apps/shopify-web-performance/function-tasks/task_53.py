import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])

    high_priority_ids = ["rec_001", "rec_002", "rec_008"]
    high_priority_titles = {
        "rec_001": "Reduce the impact of third-party scripts",
        "rec_002": "Optimize large hero images on homepage",
        "rec_008": "Reserve space for Privy pop-up banner",
    }
    errors = []

    for rec_id in high_priority_ids:
        found = None
        for rec in recommendations:
            if rec.get("id") == rec_id:
                found = rec
                break

        if found is None:
            errors.append(f"Recommendation '{rec_id}' ({high_priority_titles[rec_id]}) not found in state.")
            continue

        if found.get("status") != "resolved":
            errors.append(
                f"Recommendation '{rec_id}' ({high_priority_titles[rec_id]}) status is '{found.get('status')}', expected 'resolved'."
            )

    if errors:
        return False, " ".join(errors)

    return True, "All high-priority recommendations (rec_001, rec_002, rec_008) are correctly resolved."
