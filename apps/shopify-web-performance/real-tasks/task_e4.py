import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    tag = next((t for t in tags if t.get("name") == "TikTok Pixel"), None)
    if tag is None:
        return False, "Tag 'TikTok Pixel' not found in tagManagerTags list."

    if tag.get("status") != "inactive":
        return False, f"Expected TikTok Pixel tag status to be 'inactive', but got '{tag.get('status')}'."

    return True, "TikTok Pixel tag has been deactivated (status=inactive)."
