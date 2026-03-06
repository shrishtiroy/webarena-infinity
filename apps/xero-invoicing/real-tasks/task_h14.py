import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Harbour City Plumbing"), None)
    if not contact:
        return False, "Contact Harbour City Plumbing not found."

    ri = next((r for r in state["repeatingInvoices"]
               if r["contactId"] == contact["id"]), None)

    if not ri:
        return False, "No repeating invoice found for Harbour City Plumbing."

    if ri["frequency"] != "monthly":
        return False, f"Frequency is '{ri['frequency']}', expected 'monthly'."

    if ri["saveAs"] != "approved_for_sending":
        return False, f"saveAs is '{ri['saveAs']}', expected 'approved_for_sending'."

    hosting_line = next((li for li in ri.get("lineItems", [])
                         if li.get("itemId") == "item_004"), None)
    if not hosting_line:
        return False, "No hosting line item found."

    return True, "Monthly auto-sent hosting repeating invoice created for Harbour City Plumbing."
