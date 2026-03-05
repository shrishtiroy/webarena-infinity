import requests


SEED_REPEAT_IDS = {"rep_001", "rep_002", "rep_003", "rep_004", "rep_005"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # New repeating invoice for Horizon Media & Advertising (con_004)
    new_ri = None
    for ri in state.get("repeatingInvoices", []):
        if ri.get("contactId") == "con_004" and ri.get("id") not in SEED_REPEAT_IDS:
            new_ri = ri
            break

    if new_ri is None:
        return False, (
            "No new repeating invoice found for Horizon Media & Advertising (con_004)."
        )

    freq = new_ri.get("frequency", "")
    if freq != "monthly":
        return False, (
            f"New repeating invoice frequency is '{freq}', expected 'monthly'."
        )

    save_as = new_ri.get("saveAs", "")
    if save_as != "draft":
        return False, (
            f"New repeating invoice saveAs is '{save_as}', expected 'draft'."
        )

    start = new_ri.get("startDate", "")
    if not start.startswith("2026-04"):
        return False, (
            f"New repeating invoice startDate is '{start}', expected to start with '2026-04'."
        )

    theme = new_ri.get("brandingThemeId", "")
    if theme != "theme_standard":
        return False, (
            f"New repeating invoice brandingThemeId is '{theme}', expected 'theme_standard'."
        )

    # Check line items: 16 hours UI/UX design ($165) and 4 hours consulting ($250)
    line_items = new_ri.get("lineItems", [])
    if len(line_items) < 2:
        return False, (
            f"New repeating invoice has {len(line_items)} line items, expected at least 2."
        )

    found_design = False
    found_consulting = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 165.00) < 10.00 and qty == 16:
            found_design = True
        if abs(price - 250.00) < 10.00 and qty == 4:
            found_consulting = True

    if not found_design:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 16 and unitPrice ~$165 (UI/UX design) found. "
            f"Items: {items}."
        )

    if not found_consulting:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 4 and unitPrice ~$250 (consulting) found. "
            f"Items: {items}."
        )

    return True, (
        f"Monthly repeating invoice created for Horizon Media & Advertising: "
        f"16 hrs UI/UX design + 4 hrs consulting, saved as draft, starting April 2026, "
        f"Standard theme."
    )
