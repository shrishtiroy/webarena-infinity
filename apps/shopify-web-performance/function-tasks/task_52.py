import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])

    target_names = ["Pinterest Tag", "Snapchat Pixel", "Lucky Orange"]
    errors = []

    for target_name in target_names:
        found = None
        for tag in tags:
            if tag.get("name") == target_name:
                found = tag
                break

        if found is None:
            errors.append(f"Tag '{target_name}' not found in state.")
            continue

        if found.get("status") != "active":
            errors.append(f"Tag '{target_name}' status is '{found.get('status')}', expected 'active'.")

    if errors:
        return False, " ".join(errors)

    return True, "All inactive tags (Pinterest Tag, Snapchat Pixel, Lucky Orange) are correctly activated."
