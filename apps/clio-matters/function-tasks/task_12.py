import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "")
        if "Foster" in desc and "Evanston" in desc:
            client_ref = matter.get("clientRefNumber", "")
            if client_ref == "SLIP-2024-NEW":
                return True, f"Matter '{desc}' has clientRefNumber 'SLIP-2024-NEW' as expected."
            else:
                return False, f"Matter '{desc}' has clientRefNumber '{client_ref}', expected 'SLIP-2024-NEW'."

    return False, "No matter found with description containing 'Foster' and 'Evanston'."
