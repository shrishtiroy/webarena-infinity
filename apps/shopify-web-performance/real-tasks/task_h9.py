import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    errors = []

    expected = {
        "Horizon - Outdoors": 10,
        "Dawn (backup)": 6,
        "Prestige": 16,
    }

    for theme_name, expected_home in expected.items():
        theme = next((t for t in themes if t.get("name") == theme_name), None)
        if theme is None:
            errors.append(f"Could not find theme '{theme_name}' in themes list.")
            continue
        sections = theme.get("sectionsPerPage", {})
        actual_home = sections.get("home")
        if actual_home != expected_home:
            errors.append(f"Theme '{theme_name}' homepage sections is {actual_home}, expected {expected_home}.")

    if errors:
        return False, " ".join(errors)

    return True, "All three themes have homepage sections reduced by 2: Horizon=10, Dawn=6, Prestige=16."
