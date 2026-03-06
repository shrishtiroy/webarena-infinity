import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "Atlas Engineering Consultants"), None)
    if not contact:
        return False, "Contact Atlas Engineering Consultants not found."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and any(li.get("itemId") == "item_003" for li in i.get("lineItems", []))), None)

    if not new_inv:
        return False, "No new invoice with PM days found for Atlas Engineering."

    if new_inv["brandingThemeId"] != "theme_professional":
        return False, f"Branding theme is '{new_inv['brandingThemeId']}', expected 'theme_professional'."

    pm_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_003"), None)
    if pm_line["quantity"] != 5:
        return False, f"PM days is {pm_line['quantity']}, expected 5."

    if abs(pm_line["unitPrice"] - 1400.00) > 0.01:
        return False, f"PM rate is {pm_line['unitPrice']}, expected 1400.00."

    return True, f"Invoice {new_inv['number']} created for Atlas Engineering with Professional Services template."
