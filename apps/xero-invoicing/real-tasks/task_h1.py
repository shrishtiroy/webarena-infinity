import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "TechVault Solutions Pty Ltd"), None)
    if not contact:
        return False, "Contact TechVault Solutions not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] not in ["INV-0043", "INV-0055"]
                    and any(li.get("itemId") == "item_001" for li in i.get("lineItems", []))), None)

    if not new_inv:
        return False, "No new invoice with dev hours found for TechVault."

    dev_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_001"), None)
    if not dev_line:
        return False, "No dev-hour line item found."

    if dev_line["quantity"] != 10:
        return False, f"Dev hours quantity is {dev_line['quantity']}, expected 10."

    if abs(dev_line["unitPrice"] - 185.00) > 0.01:
        return False, f"Dev hours unit price is {dev_line['unitPrice']}, expected 185.00."

    return True, f"Invoice {new_inv['number']} created for TechVault with 10 dev hours."
