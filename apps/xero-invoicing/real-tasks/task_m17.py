import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    theme = next((t for t in state["brandingThemes"] if t["id"] == "theme_professional"), None)
    if not theme:
        return False, "Professional Services theme not found."

    expected = "All work is subject to our Master Services Agreement. Payment terms are strictly net 30 days."
    if theme.get("termsAndConditions") != expected:
        return False, f"Terms and conditions not updated correctly. Got: '{theme.get('termsAndConditions', '')[:80]}...'"

    return True, "Professional Services template terms and conditions updated."
