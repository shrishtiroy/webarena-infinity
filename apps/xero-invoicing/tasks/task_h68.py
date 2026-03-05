import requests


SEED_CN_IDS = {"cn_001", "cn_002", "cn_003", "cn_004", "cn_005"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The only quote with isInvoiced=true is QU-0027 (Stellar Education Services,
    # con_009, 3 days on-site training at $2,200).
    new_cn = None
    for cn in state.get("creditNotes", []):
        if cn.get("contactId") == "con_009" and cn.get("id") not in SEED_CN_IDS:
            new_cn = cn
            break

    if new_cn is None:
        return False, (
            "No new credit note found for Stellar Education Services (con_009)."
        )

    if new_cn.get("status") != "draft":
        return False, (
            f"New credit note status is '{new_cn.get('status')}', expected 'draft'."
        )

    # Check line item: 3 days training at ~$2,200
    line_items = new_cn.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 2200.00) < 50.00 and qty == 3:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 3 and unitPrice ~$2,200 (on-site training) found. "
            f"Items: {items}."
        )

    return True, (
        f"QU-0027 (only invoiced quote) identified. Draft credit note "
        f"'{new_cn.get('number')}' created for Stellar Education with matching line items."
    )
