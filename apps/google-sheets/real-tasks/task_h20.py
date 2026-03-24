import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, "Employees sheet (index 1) not found."

    employees = sheets[1]
    cells = employees.get("cells", {})

    # Check 1 & 2: No "Active" or "On Leave" in G column; at least one "Current" and one "Away"
    found_current = False
    found_away = False
    forbidden_values = []

    for cell_key, cell_data in cells.items():
        if cell_key.startswith("G"):
            row_part = cell_key[1:]
            if row_part.isdigit():
                row_num = int(row_part)
                if 2 <= row_num <= 26:
                    value = cell_data.get("value", "")
                    if value == "Active":
                        forbidden_values.append(f"{cell_key} still has 'Active'")
                    if value == "On Leave":
                        forbidden_values.append(f"{cell_key} still has 'On Leave'")
                    if value == "Current":
                        found_current = True
                    if value == "Away":
                        found_away = True

    if forbidden_values:
        errors.append("Found cells not updated: " + ", ".join(forbidden_values))
    if not found_current:
        errors.append("No cell in G column contains 'Current'")
    if not found_away:
        errors.append("No cell in G column contains 'Away'")

    # Check 3: Conditional formatting rule text_contains "Away" bg yellow (#ffff00)
    cf_rules = employees.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        rule_type = rule.get("type", "")
        rule_value = rule.get("value", rule.get("text", ""))
        bg = rule.get("backgroundColor", rule.get("format", {}).get("backgroundColor", ""))

        if rule_type == "text_contains" and rule_value == "Away" and bg.lower() == "#ffff00":
            found_cf = True
            break

    if not found_cf:
        errors.append(
            "No conditional format rule found with type 'text_contains', value 'Away', "
            "and backgroundColor '#ffff00'"
        )

    # Check 4: namedRanges["TeamStatus"] == "Employees!G2:G26"
    named_ranges = state.get("namedRanges", {})
    team_status = named_ranges.get("TeamStatus")
    if team_status is None:
        errors.append("Named range 'TeamStatus' not found")
    elif team_status != "Employees!G2:G26":
        errors.append(
            f"Named range 'TeamStatus' is '{team_status}', expected 'Employees!G2:G26'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
