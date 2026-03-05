import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    contacts = state.get("contacts", [])
    matching = [c for c in contacts if c.get("firstName") == "Michael" and c.get("lastName") == "Rivera"]
    if not matching:
        return False, "Contact with firstName 'Michael' and lastName 'Rivera' not found."

    contact = matching[0]

    email = contact.get("email")
    if email != "mrivera@email.com":
        return False, f"Expected contact email 'mrivera@email.com', got '{email}'."

    phone = contact.get("phone")
    if phone != "(555) 999-1234":
        return False, f"Expected contact phone '(555) 999-1234', got '{phone}'."

    return True, "Contact 'Michael Rivera' exists with correct email 'mrivera@email.com' and phone '(555) 999-1234'."
