import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Gonzalez divorce (not paternity)
    # matter_28: "Gonzalez Divorce - Contested dissolution"
    # matter_38: "Gonzalez Paternity"
    gonzalez_divorce = next(
        (m for m in state.get("matters", [])
         if "gonzalez" in m.get("description", "").lower()
         and "divorce" in m.get("description", "").lower()
         and "paternity" not in m.get("description", "").lower()),
        None
    )

    if gonzalez_divorce is None:
        return False, "Could not find Gonzalez divorce matter (not the paternity case)."

    matter_id = gonzalez_divorce["id"]

    # Check Thomas O'Brien (user_4) is a notification recipient
    notifications = gonzalez_divorce.get("notifications", [])
    obrien_notification = next(
        (n for n in notifications if n.get("userId") == "user_4"),
        None
    )

    if obrien_notification is None:
        # Also check if notifications is a flat list of user IDs
        if "user_4" not in notifications:
            notif_users = [n.get("userId") if isinstance(n, dict) else n for n in notifications]
            errors.append(
                f"Thomas O'Brien (user_4) not found in notification recipients. "
                f"Current recipients: {notif_users}."
            )

    # Check permissions restricted to Family Law Division (group_2)
    permissions = gonzalez_divorce.get("permissions", {})
    perm_type = permissions.get("type")
    group_ids = permissions.get("groupIds", [])

    if perm_type != "specific":
        errors.append(
            f"Permissions type is '{perm_type}', expected 'specific'."
        )

    if "group_2" not in group_ids:
        errors.append(
            f"Family Law Division (group_2) not in permission groups. "
            f"Current groups: {group_ids}."
        )

    if errors:
        return False, (
            f"Gonzalez divorce matter ({matter_id}) not updated correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"Gonzalez divorce matter ({matter_id}) has Thomas O'Brien as notification "
        f"recipient and permissions restricted to Family Law Division."
    )
