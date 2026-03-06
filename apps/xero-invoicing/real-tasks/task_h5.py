import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Bright Spark Electrical"), None)
    if not contact:
        return False, "Contact Bright Spark Electrical not found."

    ri = next((r for r in state["repeatingInvoices"]
               if r["contactId"] == contact["id"]), None)

    if not ri:
        return False, "No repeating invoice found for Bright Spark Electrical."

    if ri["frequency"] != "monthly":
        return False, f"Frequency is '{ri['frequency']}', expected 'monthly'."

    hosting_line = next((li for li in ri.get("lineItems", [])
                         if li.get("itemId") == "item_004"), None)
    if not hosting_line:
        return False, "No hosting line item found in repeating invoice."

    return True, "Monthly hosting repeating invoice created for Bright Spark Electrical."
