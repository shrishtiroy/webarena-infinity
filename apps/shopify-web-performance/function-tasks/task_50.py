import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    store_info = state.get("storeInfo", {})
    password_protected = store_info.get("passwordProtected")

    if password_protected is not True:
        return False, f"passwordProtected is {password_protected}, expected True."

    return True, "Password protection is correctly enabled."
