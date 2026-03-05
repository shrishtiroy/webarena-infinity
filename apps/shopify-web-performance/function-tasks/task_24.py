import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    prestige = None
    for theme in themes:
        if theme.get("name") == "Prestige":
            prestige = theme
            break

    if prestige is None:
        return False, "Theme 'Prestige' not found in state."

    sections = prestige.get("sectionsPerPage", {})
    blog_val = sections.get("blog")
    if blog_val != 8:
        return False, f"Prestige sectionsPerPage['blog'] is {blog_val}, expected 8."

    return True, "Blog sections for 'Prestige' correctly increased to 8."
