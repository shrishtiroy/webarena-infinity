import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    errors = []

    # These inactive tags should have been removed entirely
    removed_tags = ["Pinterest Tag", "Snapchat Pixel", "Lucky Orange"]
    for tag_name in removed_tags:
        found = next((t for t in tags if t.get("name") == tag_name), None)
        if found is not None:
            errors.append(f"Inactive tag '{tag_name}' should have been removed but still exists.")

    # Google Ads Conversion and TikTok Pixel (advertising) should be deactivated
    deactivated_tags = ["Google Ads Conversion", "TikTok Pixel"]
    for tag_name in deactivated_tags:
        tag = next((t for t in tags if t.get("name") == tag_name), None)
        if tag is None:
            errors.append(f"Tag '{tag_name}' not found in tag manager tags list.")
        elif tag.get("status") != "inactive":
            errors.append(f"Tag '{tag_name}' status is '{tag.get('status')}', expected 'inactive'.")

    # Meta Pixel should remain active
    meta = next((t for t in tags if t.get("name") == "Meta Pixel"), None)
    if meta is None:
        errors.append("Tag 'Meta Pixel' not found in tag manager tags list.")
    elif meta.get("status") != "active":
        errors.append(f"Tag 'Meta Pixel' status is '{meta.get('status')}', expected 'active'.")

    if errors:
        return False, " ".join(errors)

    return True, "All inactive tags removed, advertising tags (except Meta Pixel) deactivated, Meta Pixel remains active."
