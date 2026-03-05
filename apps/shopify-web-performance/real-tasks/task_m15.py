import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    errors = []

    target_tags = ["Pinterest Tag", "Snapchat Pixel"]
    for target_name in target_tags:
        found = None
        for tag in tags:
            if tag.get("name") == target_name:
                found = tag
                break
        if found is None:
            errors.append(f"Tag '{target_name}' not found in tagManagerTags list.")
            continue
        if found.get("status") != "active":
            errors.append(f"Tag '{target_name}' status is '{found.get('status')}', expected 'active'.")

    if errors:
        return False, " ".join(errors)

    return True, "Both Pinterest Tag and Snapchat Pixel tags are active."
