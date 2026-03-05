import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("brandingThemes", [])
    target = None
    for theme in themes:
        if theme.get("name") == "Corporate":
            target = theme
            break

    if target is None:
        return False, "No branding theme with name 'Corporate' found."

    # Check showPaymentAdvice is False
    show_payment_advice = target.get("showPaymentAdvice")
    if show_payment_advice is not False:
        return False, f"Corporate theme showPaymentAdvice is {show_payment_advice}, expected False."

    # Check paymentTerms
    payment_terms = target.get("paymentTerms", "")
    if payment_terms != "Payment due within 7 business days":
        return False, f"Corporate theme paymentTerms is '{payment_terms}', expected 'Payment due within 7 business days'."

    return True, "Branding theme 'Corporate' created with showPaymentAdvice=False and correct payment terms."
