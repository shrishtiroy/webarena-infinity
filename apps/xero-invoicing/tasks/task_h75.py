import requests


SEED_QUOTE_IDS = {
    "quo_001", "quo_002", "quo_003", "quo_004",
    "quo_005", "quo_006", "quo_007", "quo_008",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Professional Services theme: seed has showTaxNumber=true, showPaymentAdvice=true
    # After toggle: showTaxNumber=false, showPaymentAdvice=false
    theme = None
    for t in state.get("brandingThemes", []):
        if t.get("id") == "theme_professional":
            theme = t
            break

    if theme is None:
        return False, "Professional Services theme not found."

    if theme.get("showTaxNumber") is not False:
        return False, (
            f"Professional Services showTaxNumber is {theme.get('showTaxNumber')}, "
            f"expected False (toggled from True)."
        )

    if theme.get("showPaymentAdvice") is not False:
        return False, (
            f"Professional Services showPaymentAdvice is {theme.get('showPaymentAdvice')}, "
            f"expected False (toggled from True)."
        )

    # New quote for Sapphire Bay Resort (con_018)
    new_quo = None
    for q in state.get("quotes", []):
        if q.get("contactId") == "con_018" and q.get("id") not in SEED_QUOTE_IDS:
            new_quo = q
            break

    if new_quo is None:
        return False, (
            "No new quote found for Sapphire Bay Resort (con_018)."
        )

    if new_quo.get("status") != "sent":
        return False, (
            f"New quote status is '{new_quo.get('status')}', expected 'sent'."
        )

    # Check line item: security audit at ~$5,500
    line_items = new_quo.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        if abs(price - 5500.00) < 100.00:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with unitPrice ~$5,500 (security audit) found. Items: {items}."
        )

    return True, (
        f"Professional Services theme toggled (tax number + payment advice both hidden). "
        f"Quote '{new_quo.get('number')}' for Sapphire Bay Resort (security audit) sent."
    )
