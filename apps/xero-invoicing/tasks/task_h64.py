import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The only awaiting-payment invoice with tax-inclusive + Simple Clean is
    # INV-0049 (Coastal Living Interiors, con_011).
    inv = None
    for i in state.get("invoices", []):
        if i.get("number") == "INV-0049":
            inv = i
            break

    if inv is None:
        return False, "Invoice INV-0049 not found."

    tax_mode = inv.get("taxMode", "")
    if tax_mode != "exclusive":
        return False, (
            f"INV-0049 taxMode is '{tax_mode}', expected 'exclusive'."
        )

    theme = inv.get("brandingThemeId", "")
    if theme != "theme_professional":
        return False, (
            f"INV-0049 brandingThemeId is '{theme}', expected 'theme_professional'."
        )

    return True, (
        "INV-0049 (the only awaiting-payment + tax-inclusive + Simple Clean invoice) "
        "edited: taxMode changed to exclusive, branding changed to Professional Services."
    )
