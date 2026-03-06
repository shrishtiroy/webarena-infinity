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
                   and cn["number"] not in ["CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"]
                   and any(li.get("itemId") == "item_011" for li in cn.get("lineItems", []))), None)

    if not new_cn:
        return False, "No new credit note with Widget A found for Greenfield Organics."

    if new_cn["status"] != "awaiting_payment":
        return False, f"Credit note status is '{new_cn['status']}', expected 'awaiting_payment' (approved)."

    widget_line = next((li for li in new_cn["lineItems"] if li.get("itemId") == "item_011"), None)
    if widget_line["quantity"] != 5:
        return False, f"Widget A quantity is {widget_line['quantity']}, expected 5."

    if abs(widget_line["unitPrice"] - 24.95) > 0.01:
        return False, f"Widget A unit price is {widget_line['unitPrice']}, expected 24.95."

    return True, f"Credit note {new_cn['number']} for 5 Widget A units created and approved."
