import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Add a conditional formatting rule on the Inventory sheet to highlight stock values below 20 with red background (#ffc7ce)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Inventory sheet is at index 2
    sheets = state.get("sheets", [])
    if len(sheets) < 3:
        return False, f"Expected at least 3 sheets, found {len(sheets)}."

    inventory = sheets[2]
    cond_formats = inventory.get("conditionalFormats", [])

    if not cond_formats:
        return False, "No conditional formatting rules found on the Inventory sheet."

    for rule in cond_formats:
        rule_type = rule.get("type", "").lower()
        rule_value = str(rule.get("value", ""))
        bg_color = rule.get("backgroundColor", "").lower()

        if rule_type == "less_than" and rule_value == "20" and bg_color == "#ffc7ce":
            # Verify range covers D column
            rule_range = rule.get("range", "")
            if "D" in rule_range.upper():
                return True, f"Found matching conditional format rule: type={rule_type}, value={rule_value}, bg={bg_color}, range={rule_range}."
            else:
                return False, f"Found a matching rule but range does not cover column D. Range: {rule_range}."

    return False, (
        f"No conditional format rule found with type='less_than', value='20', backgroundColor='#ffc7ce'. "
        f"Found {len(cond_formats)} rule(s): {cond_formats}"
    )
