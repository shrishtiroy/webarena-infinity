import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    tag_names = [tag.get("name", "") for tag in tags]

    still_present = []
    for target in ["Pinterest Tag", "Snapchat Pixel"]:
        if target in tag_names:
            still_present.append(target)

    if still_present:
        return False, f"The following tags are still present in tagManagerTags: {', '.join(still_present)}."

    return True, "Both Pinterest Tag and Snapchat Pixel have been removed from the tag manager."
