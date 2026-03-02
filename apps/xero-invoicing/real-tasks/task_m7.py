import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    repeating_invoices = state.get("repeatingInvoices", [])
    rep = None
    for r in repeating_invoices:
        if r.get("id") == "rep_001":
            rep = r
            break

    if rep is None:
        return False, "Repeating invoice with id 'rep_001' not found."

    end_date = rep.get("endDate")
    if end_date != "2027-06-30":
        return False, f"Repeating invoice rep_001 endDate is '{end_date}', expected '2027-06-30'."

    return True, "Greenfield Organics repeating invoice (rep_001) end date has been set to 2027-06-30."
