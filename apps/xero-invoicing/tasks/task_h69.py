import requests


SEED_INVOICE_IDS = {
    "inv_000", "inv_001", "inv_002", "inv_003", "inv_004", "inv_005",
    "inv_006", "inv_007", "inv_008", "inv_009", "inv_010", "inv_011",
    "inv_012", "inv_013", "inv_014", "inv_015", "inv_016", "inv_017",
    "inv_018", "inv_019", "inv_020", "inv_021", "inv_022", "inv_023",
    "inv_024", "inv_025",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The only non-AUD invoice is INV-0066 (NZD, Wellington & Partners, con_016).
    # Copy it, then edit copy: currency=AUD, brandingThemeId=theme_standard.
    new_inv = None
    for inv in state.get("invoices", []):
        if inv.get("contactId") == "con_016" and inv.get("id") not in SEED_INVOICE_IDS:
            new_inv = inv
            break

    if new_inv is None:
        return False, (
            "No new invoice found for Wellington & Partners (con_016)."
        )

    currency = new_inv.get("currency", "")
    if currency != "AUD":
        return False, (
            f"New invoice currency is '{currency}', expected 'AUD'."
        )

    theme = new_inv.get("brandingThemeId", "")
    if theme != "theme_standard":
        return False, (
            f"New invoice brandingThemeId is '{theme}', expected 'theme_standard'."
        )

    # Should have consulting line items from the original INV-0066
    line_items = new_inv.get("lineItems", [])
    if not line_items:
        return False, "New invoice has no line items."

    return True, (
        f"INV-0066 (only non-AUD invoice) copied. New invoice '{new_inv.get('number')}' "
        f"edited: currency changed to AUD, branding changed to Standard."
    )
