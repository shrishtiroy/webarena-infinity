import requests


SEED_THEME_IDS = {"theme_standard", "theme_professional", "theme_simple", "theme_retail"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check for 'Express' branding theme
    express_theme = None
    for t in state.get("brandingThemes", []):
        if t.get("name") == "Express":
            express_theme = t
            break

    if express_theme is None:
        return False, "No branding theme named 'Express' found."

    if express_theme.get("paymentTerms") != "Due on receipt":
        return False, (
            f"Express theme paymentTerms is '{express_theme.get('paymentTerms')}', "
            f"expected 'Due on receipt'."
        )

    if express_theme.get("showTaxNumber") is not True:
        return False, (
            f"Express theme showTaxNumber is {express_theme.get('showTaxNumber')}, "
            f"expected True."
        )

    if express_theme.get("showPaymentAdvice") is not True:
        return False, (
            f"Express theme showPaymentAdvice is {express_theme.get('showPaymentAdvice')}, "
            f"expected True."
        )

    # Check rep_001 (Greenfield Organics) uses the Express theme
    ri = None
    for r in state.get("repeatingInvoices", []):
        if r.get("id") == "rep_001":
            ri = r
            break

    if ri is None:
        return False, "Repeating invoice rep_001 not found."

    if ri.get("brandingThemeId") != express_theme.get("id"):
        return False, (
            f"rep_001 brandingThemeId is '{ri.get('brandingThemeId')}', "
            f"expected '{express_theme.get('id')}' (Express)."
        )

    return True, (
        f"Branding theme 'Express' created (Due on receipt, tax number + payment advice shown). "
        f"Greenfield Organics repeating invoice updated to use Express theme."
    )
