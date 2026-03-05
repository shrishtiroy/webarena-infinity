import requests


SEED_CN_IDS = {"cn_001", "cn_002", "cn_003", "cn_004", "cn_005"}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Contact with most unpaid invoices: CloudNine Analytics (con_007) with 2
    # (INV-0047 and INV-0062). All others have at most 1.
    new_cn = None
    for cn in state.get("creditNotes", []):
        if cn.get("contactId") == "con_007" and cn.get("id") not in SEED_CN_IDS:
            new_cn = cn
            break

    if new_cn is None:
        return False, (
            "No new credit note found for CloudNine Analytics (con_007), "
            "the contact with the most unpaid invoices."
        )

    # Should be approved (not draft)
    if new_cn.get("status") == "draft":
        return False, (
            f"New credit note '{new_cn.get('number')}' is still draft — not approved."
        )

    # Check line item: 1 month cloud hosting at ~$299
    line_items = new_cn.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 299.00) < 10.00 and qty == 1:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 1 and unitPrice ~$299 (cloud hosting) found. "
            f"Items: {items}."
        )

    return True, (
        f"CloudNine Analytics (most unpaid invoices: 2) identified. "
        f"Credit note '{new_cn.get('number')}' created for 1 month hosting, approved."
    )
