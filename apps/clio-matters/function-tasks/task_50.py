import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00001"]
    if not matching:
        return False, "Matter with number '00001' not found."

    matter = matching[0]
    custom_fields = matter.get("customFields", {})
    cf_7 = custom_fields.get("cf_7")
    if cf_7 != "Hon. Patricia Williams":
        return False, f"Expected matter '00001' customFields.cf_7 (Judge Assigned) to be 'Hon. Patricia Williams', got '{cf_7}'."

    return True, "Matter '00001-Patterson' customFields.cf_7 (Judge Assigned) is correctly set to 'Hon. Patricia Williams'."
