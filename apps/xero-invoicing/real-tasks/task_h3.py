import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Greenfield Organics"), None)
    if not contact:
        return False, "Contact Greenfield Organics not found."

    new_cn = next((cn for cn in state["creditNotes"]
                   if cn["contactId"] == contact["id"]
                   and cn["number"] not in ["CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"]), None)

    if not new_cn:
        return False, "No new credit note found for Greenfield Organics."

    has_100_line = any(abs(li["unitPrice"] - 100.00) < 0.01 and li["quantity"] == 1
                       for li in new_cn.get("lineItems", []))
    if not has_100_line:
        return False, "Credit note does not contain a $100 line item."

    return True, f"Credit note {new_cn['number']} created for Greenfield Organics."
