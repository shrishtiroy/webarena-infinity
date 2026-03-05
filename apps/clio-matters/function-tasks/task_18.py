import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00005":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00005'."

    custom_fields = matter.get("customFields", {})
    cf_1_value = custom_fields.get("cf_1")

    if cf_1_value != "SM-2024-CV-19876":
        return False, f"Expected matter '00005-Doyle' customFields.cf_1 (Court Case Number) to be 'SM-2024-CV-19876', but got '{cf_1_value}'."

    return True, "Matter '00005-Doyle' customFields.cf_1 (Court Case Number) is correctly set to 'SM-2024-CV-19876'."
