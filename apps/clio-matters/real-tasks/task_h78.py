import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Seed hourly templates: Criminal Defense - Misdemeanor, Family Law - Divorce,
    # Corporate Transaction - M&A. They should all now have contingency billing at 25%.
    hourly_templates = ["Criminal Defense", "Family Law", "Corporate Transaction"]

    errors = []
    updated_count = 0
    for t in state.get("matterTemplates", []):
        name = t.get("name") or ""
        is_hourly_seed = any(h in name for h in hourly_templates)
        if is_hourly_seed:
            if t.get("billingMethod") != "contingency":
                errors.append(
                    f"'{name}': billing is '{t.get('billingMethod')}', expected 'contingency'."
                )
            elif t.get("contingencyRate") != 25:
                errors.append(
                    f"'{name}': contingency rate is {t.get('contingencyRate')}%, expected 25%."
                )
            else:
                updated_count += 1

    if updated_count < 3 and not errors:
        errors.append(f"Expected 3 hourly templates updated, found {updated_count}.")

    if errors:
        return False, " ".join(errors)

    return True, "All hourly billing templates changed to contingency at 25%."
