import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    notifications = state.get("notificationSettings", {})

    matter_updates = notifications.get("matter_updates")
    if matter_updates is not False:
        return False, f"Expected notificationSettings matter_updates to be False, got '{matter_updates}'."

    trust_balance = notifications.get("trust_balance")
    if trust_balance is not True:
        return False, f"Expected notificationSettings trust_balance to be True, got '{trust_balance}'."

    return True, "Notification settings correct: matter_updates is False and trust_balance is True."
