import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Sapphire Bay Resort"), None)
    if not contact:
        return False, "Contact Sapphire Bay Resort not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] != "INV-0054"
                    and any(li.get("itemId") == "item_006" for li in i.get("lineItems", []))), None)

    if not new_inv:
        return False, "No new invoice with training found for Sapphire Bay Resort."

    training_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_006"), None)
    if training_line["quantity"] != 3:
        return False, f"Training days is {training_line['quantity']}, expected 3."

    if abs(training_line["unitPrice"] - 2200.00) > 0.01:
        return False, f"Training rate is {training_line['unitPrice']}, expected 2200.00."

    return True, f"Invoice {new_inv['number']} created for Sapphire Bay Resort with 3 training days."
