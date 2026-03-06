import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    quo = next((q for q in state["quotes"] if q["number"] == "QU-0022"), None)
    if not quo:
        return False, "Quote QU-0022 not found."

    if not quo.get("isInvoiced"):
        return False, "Quote QU-0022 is not marked as invoiced."

    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == quo["contactId"]
                    and i["status"] == "draft"
                    and abs(i["total"] - quo["total"]) < 0.01
                    and i["number"] not in ["INV-0042", "INV-0045"]), None)

    if not new_inv:
        return False, "No new draft invoice found for Pinnacle Construction matching quote total."

    return True, f"Quote QU-0022 converted to invoice {new_inv['number']}."
