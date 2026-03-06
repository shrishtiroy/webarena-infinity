import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Southern Cross Veterinary"), None)
    if not contact:
        return False, "Contact Southern Cross Veterinary not found."

    new_quo = next((q for q in state["quotes"]
                    if q["contactId"] == contact["id"]), None)

    if not new_quo:
        return False, "No quote found for Southern Cross Veterinary."

    consult_line = next((li for li in new_quo.get("lineItems", [])
                         if li.get("itemId") == "item_002"), None)
    if not consult_line:
        return False, "No consulting line item found in quote."

    if consult_line["quantity"] != 8:
        return False, f"Consulting quantity is {consult_line['quantity']}, expected 8."

    if abs(consult_line["unitPrice"] - 250.00) > 0.01:
        return False, f"Consulting rate is {consult_line['unitPrice']}, expected 250.00."

    return True, f"Quote {new_quo['number']} created for Southern Cross Veterinary."
