import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    src = next((i for i in state["invoices"] if i["number"] == "INV-0046"), None)
    if not src:
        return False, "Original invoice INV-0046 not found."

    copies = [i for i in state["invoices"]
              if i["contactId"] == src["contactId"]
              and i["status"] == "draft"
              and i["number"] != "INV-0046"
              and abs(i["total"] - src["total"]) < 0.01]

    if not copies:
        return False, "No draft copy of INV-0046 found for the same contact."

    copy = copies[0]
    if copy["amountPaid"] != 0:
        return False, f"Copy has amountPaid={copy['amountPaid']}, expected 0."

    return True, f"Invoice INV-0046 copied successfully as {copy['number']}."
