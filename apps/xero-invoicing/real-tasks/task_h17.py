import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Outback Adventures Tourism"), None)
    if not contact:
        return False, "Contact Outback Adventures Tourism not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] != "INV-0065"), None)

    if not new_inv:
        return False, "No new invoice found for Outback Adventures Tourism."

    item_ids = [li.get("itemId") for li in new_inv.get("lineItems", [])]
    if "item_009" not in item_ids:
        return False, "Invoice missing security audit line item."

    if "item_010" not in item_ids:
        return False, "Invoice missing data migration line item."

    return True, f"Invoice {new_inv['number']} created for Outback Adventures with audit and migration."
