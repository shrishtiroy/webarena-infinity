import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    recommendations = state.get("recommendations", [])

    low_priority_open_recs = {
        "Enable pagination for large collections": "rec_006",
        "Preload web fonts": "rec_010",
    }

    errors = []
    for title, rec_id in low_priority_open_recs.items():
        found = None
        for rec in recommendations:
            if rec.get("title") == title:
                found = rec
                break
        if found is None:
            errors.append(f"Recommendation '{title}' ({rec_id}) not found in recommendations list.")
            continue
        if found.get("status") != "dismissed":
            errors.append(f"Recommendation '{title}' status is '{found.get('status')}', expected 'dismissed'.")

    if errors:
        return False, " ".join(errors)

    return True, "All low-priority open recommendations (rec_006 and rec_010) have been dismissed."
