import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    target = None
    for inv in invoices:
        if inv.get("number") == "INV-0058":
            target = inv
            break

    if target is None:
        return False, "Could not find invoice with number 'INV-0058'."

    reference = target.get("reference", "")
    if reference != "MRW-WEB-MARCH":
        return False, f"Expected reference 'MRW-WEB-MARCH' on INV-0058, but found '{reference}'."

    return True, "Invoice INV-0058 has reference 'MRW-WEB-MARCH'."
