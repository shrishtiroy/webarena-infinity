import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Wellington & Partners Accounting"), None)
    if not contact:
        return False, "Contact Wellington & Partners not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] != "INV-0066"
                    and i["currency"] == "USD"), None)

    if not new_inv:
        return False, "No new USD invoice found for Wellington & Partners."

    consult_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_002"), None)
    if not consult_line:
        return False, "No consulting line item found."

    if consult_line["quantity"] != 12:
        return False, f"Consulting hours is {consult_line['quantity']}, expected 12."

    if abs(consult_line["unitPrice"] - 250.00) > 0.01:
        return False, f"Consulting rate is {consult_line['unitPrice']}, expected 250.00."

    return True, f"Invoice {new_inv['number']} created for Wellington & Partners in USD."
