import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    tag_names = [tag.get("name", "") for tag in tags]

    inactive_tags = ["Pinterest Tag", "Snapchat Pixel", "Lucky Orange"]
    still_present = [t for t in inactive_tags if t in tag_names]

    if still_present:
        return False, f"Inactive tags still present in tag manager: {', '.join(still_present)}."

    return True, "All inactive tags (Pinterest Tag, Snapchat Pixel, Lucky Orange) have been removed from the tag manager."
