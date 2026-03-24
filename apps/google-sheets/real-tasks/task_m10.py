import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Add conditional formatting on Employees sheet for salaries above 150000 with green bg and dark green text."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Employees sheet is at index 1
    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, f"Expected at least 2 sheets, found {len(sheets)}."

    employees = sheets[1]
    cond_formats = employees.get("conditionalFormats", [])

    if not cond_formats:
        return False, "No conditional formatting rules found on the Employees sheet."

    for rule in cond_formats:
        rule_type = rule.get("type", "").lower()
        rule_value = str(rule.get("value", ""))
        bg_color = rule.get("backgroundColor", "").lower()
        font_color = rule.get("fontColor", "").lower()

        if (
            rule_type == "greater_than"
            and rule_value == "150000"
            and bg_color == "#c6efce"
            and font_color == "#006100"
        ):
            return True, (
                f"Found matching conditional format rule: type={rule_type}, value={rule_value}, "
                f"backgroundColor={bg_color}, fontColor={font_color}."
            )

    return False, (
        f"No conditional format rule found with type='greater_than', value='150000', "
        f"backgroundColor='#c6efce', fontColor='#006100'. "
        f"Found {len(cond_formats)} rule(s): {cond_formats}"
    )
