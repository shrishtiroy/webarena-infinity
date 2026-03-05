import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    tags = state.get("tagManagerTags", [])
    errors = []

    # Hotjar and TikTok apps should be removed
    for substring in ["Hotjar", "TikTok"]:
        found = next((a for a in apps if substring in a.get("name", "")), None)
        if found is not None:
            errors.append(f"App '{found.get('name')}' should have been removed but still exists.")

    # Hotjar Tracking and TikTok Pixel tags should be removed
    for tag_name in ["Hotjar Tracking", "TikTok Pixel"]:
        found = next((t for t in tags if t.get("name") == tag_name), None)
        if found is not None:
            errors.append(f"Tag '{tag_name}' should have been removed but still exists.")

    if errors:
        return False, " ".join(errors)

    return True, "Hotjar and TikTok apps removed along with their matching tracking tags."
