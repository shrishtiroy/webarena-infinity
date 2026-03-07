import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    cruz_metro_matters = []
    for matter in matters:
        desc = matter.get("description", "") or ""
        display = matter.get("displayNumber", "") or ""
        combined = desc + " " + display
        if "Cruz" in combined and "Metro Transit" in combined:
            cruz_metro_matters.append(matter)
        elif "Cruz" in combined and "Metro" in combined:
            cruz_metro_matters.append(matter)

    if len(cruz_metro_matters) >= 2:
        return True, f"Found {len(cruz_metro_matters)} matters matching 'Cruz' and 'Metro Transit' (original + duplicate)."
    elif len(cruz_metro_matters) == 1:
        return False, "Only found 1 matter matching 'Cruz' and 'Metro Transit'. Expected at least 2 (original + duplicate)."
    else:
        return False, "Could not find any matter matching 'Cruz' and 'Metro Transit' in state."
