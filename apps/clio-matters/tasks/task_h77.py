import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Okafor burn injury case
    matter = next(
        (m for m in state.get("matters", [])
         if "okafor" in m.get("description", "").lower()
         and ("homecomfort" in m.get("description", "").lower()
              or "burn" in m.get("description", "").lower()
              or "heater" in m.get("description", "").lower())),
        None,
    )
    if matter is None:
        return False, "Okafor burn injury case not found."

    # 1. Check permissions restricted to Litigation Team (group_1)
    perms = matter.get("permissions", {})
    if perms.get("type") != "specific":
        errors.append(
            f"Permissions type is '{perms.get('type')}', expected 'specific'."
        )
    elif "group_1" not in perms.get("groupIds", []):
        errors.append(
            f"Litigation Team (group_1) not in permission groups. "
            f"Groups: {perms.get('groupIds')}."
        )

    # 2. Check James Cooper (user_14) is blocked
    blocked = matter.get("blockedUsers", [])
    if "user_14" not in blocked:
        errors.append(
            f"James Cooper (user_14) not in blocked users. Blocked: {blocked}."
        )

    # 3. Check notification recipients include Kevin Nakamura (user_6) and Angela Martinez (user_9)
    notifications = matter.get("notifications", [])
    notif_user_ids = set()
    for n in notifications:
        uid = n.get("userId")
        if uid:
            notif_user_ids.add(uid)

    if "user_6" not in notif_user_ids:
        errors.append(
            f"Kevin Nakamura (user_6) not in notification recipients. "
            f"Recipients: {list(notif_user_ids)}."
        )
    if "user_9" not in notif_user_ids:
        errors.append(
            f"Angela Martinez (user_9) not in notification recipients. "
            f"Recipients: {list(notif_user_ids)}."
        )

    if errors:
        return False, (
            "Okafor case permissions/notifications not set correctly. " + " | ".join(errors)
        )

    return True, (
        "Okafor burn injury case correctly updated: permissions restricted to "
        "Litigation Team, James Cooper blocked, Kevin Nakamura and Angela Martinez "
        "added as notification recipients."
    )
