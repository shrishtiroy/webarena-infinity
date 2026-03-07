import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    count = 0
    for matter in matters:
        contact_name = matter.get("contactName", "")
        if contact_name == "Samantha Cruz":
            count += 1

    if count >= 2:
        return True, f"Found {count} matters with contactName 'Samantha Cruz' (>= 2), confirming duplication."
    else:
        return False, f"Found {count} matter(s) with contactName 'Samantha Cruz', expected >= 2 to confirm duplication."
