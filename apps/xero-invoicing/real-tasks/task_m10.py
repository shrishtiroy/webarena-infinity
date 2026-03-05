import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    branding_themes = state.get("brandingThemes", [])
    theme = None
    for t in branding_themes:
        if t.get("name") == "Modern Minimalist":
            theme = t
            break

    if theme is None:
        return False, "No branding theme named 'Modern Minimalist' found."

    payment_terms = theme.get("paymentTerms")
    if payment_terms != "Net 14 days":
        return False, f"Branding theme 'Modern Minimalist' paymentTerms is '{payment_terms}', expected 'Net 14 days'."

    is_default = theme.get("isDefault")
    if is_default is True:
        return False, "Branding theme 'Modern Minimalist' isDefault is True, expected False."

    return True, "Branding theme 'Modern Minimalist' has been created with payment terms 'Net 14 days' and is not set as default."
