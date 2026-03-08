import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Seed closed matters: Midwest Manufacturing, GlobalTrade Logistics, O'Brien
    closed_names = ["Midwest Manufacturing", "GlobalTrade", "O'Brien"]

    errors = []
    # Check they are NOT in the matters list
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        for name in closed_names:
            if name in desc:
                errors.append(f"'{desc}' should have been deleted but is still in matters list.")
                break

    # Check they ARE in the deletedMatters list
    deleted_descs = [dm.get("description") or "" for dm in state.get("deletedMatters", [])]
    for name in closed_names:
        found = any(name in d for d in deleted_descs)
        if not found:
            errors.append(f"'{name}' not found in deleted matters.")

    if errors:
        return False, " ".join(errors)

    return True, "All closed matters (Midwest, GlobalTrade, O'Brien) deleted."
