import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    quotes = state.get("quotes", [])

    # Find the original Atlas Engineering quote
    original = None
    for q in quotes:
        if q.get("number") == "QU-0024":
            original = q
            break

    if original is None:
        return False, "Could not find original quote with number 'QU-0024'."

    atlas_contact_id = original.get("contactId", "")
    if atlas_contact_id != "con_025":
        return False, f"Expected original quote QU-0024 to have contactId 'con_025', but found '{atlas_contact_id}'."

    # Find a new quote (not QU-0024) with the same contactId
    duplicate = None
    for q in quotes:
        if q.get("number") == "QU-0024":
            continue
        if q.get("contactId") == "con_025":
            duplicate = q
            break

    if duplicate is None:
        return False, "Could not find a duplicated quote for Atlas Engineering (contactId 'con_025') other than QU-0024."

    dup_status = duplicate.get("status", "")
    if dup_status != "draft":
        return False, f"Expected duplicated quote status 'draft', but found '{dup_status}'."

    line_items = duplicate.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"Expected duplicated quote to have at least one line item, but found {len(line_items)}."

    return True, f"Atlas Engineering quote duplicated successfully. New quote '{duplicate.get('number')}' is a draft with {len(line_items)} line item(s)."
