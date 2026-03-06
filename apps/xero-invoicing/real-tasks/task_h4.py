import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "TechVault Solutions Pty Ltd"), None)
    if not contact:
        return False, "Contact TechVault Solutions not found."

    new_cn = next((cn for cn in state["creditNotes"]
                   if cn["contactId"] == contact["id"]
                   and cn["number"] not in ["CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"]), None)

    if not new_cn:
        return False, "No new credit note found for TechVault."

    if new_cn["status"] != "awaiting_payment":
        return False, f"Credit note status is '{new_cn['status']}', expected 'awaiting_payment' (approved)."

    rate_line = next((li for li in new_cn.get("lineItems", [])
                      if abs(li["unitPrice"] - 25.00) < 0.01 and li["quantity"] == 4), None)
    if not rate_line:
        return False, "Credit note does not contain a 4-hour $25/hr line item."

    return True, f"Credit note {new_cn['number']} created and approved for TechVault."
