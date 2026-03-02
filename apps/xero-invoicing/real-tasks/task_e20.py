import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    branding_themes = state.get("brandingThemes", [])
    for theme in branding_themes:
        if theme.get("id") == "theme_standard":
            show_tax_number = theme.get("showTaxNumber")
            if show_tax_number is not False:
                return False, f"Standard template still shows ABN. showTaxNumber is {show_tax_number}."
            return True, "ABN has been successfully hidden on the Standard template."

    return False, "Branding theme with id 'theme_standard' not found."
