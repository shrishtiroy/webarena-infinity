import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The only repeating invoice for a WA client is rep_004
    # (Vanguard Security Systems, 60 William Street, Perth WA 6000).
    ri = None
    for r in state.get("repeatingInvoices", []):
        if r.get("id") == "rep_004":
            ri = r
            break

    if ri is None:
        return False, "Repeating invoice rep_004 not found."

    theme = ri.get("brandingThemeId", "")
    if theme != "theme_retail":
        return False, (
            f"rep_004 brandingThemeId is '{theme}', expected 'theme_retail'."
        )

    freq = ri.get("frequency", "")
    if freq != "quarterly":
        return False, (
            f"rep_004 frequency is '{freq}', expected 'quarterly'."
        )

    return True, (
        "rep_004 (Vanguard Security Systems, Perth WA) updated: "
        "branding theme set to Retail, frequency changed to quarterly."
    )
