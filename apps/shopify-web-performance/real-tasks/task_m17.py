import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    high_impact_substrings = ["Recharge", "Privy", "Hotjar"]

    errors = []
    for substring in high_impact_substrings:
        found = None
        for app in apps:
            if substring in app.get("name", ""):
                found = app
                break
        if found is None:
            errors.append(f"No app containing '{substring}' found in apps list.")
            continue
        if found.get("status") != "disabled":
            errors.append(f"App '{found.get('name')}' status is '{found.get('status')}', expected 'disabled'.")
        if found.get("loadsOnStorefront") is not False:
            errors.append(f"App '{found.get('name')}' loadsOnStorefront is {found.get('loadsOnStorefront')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "All high performance impact apps (Recharge, Privy, Hotjar) are disabled with loadsOnStorefront set to False."
