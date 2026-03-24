import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        errors.append("Employees sheet (index 1) not found")
        return False, "; ".join(errors)

    employees = sheets[1]
    cells = employees.get("cells", {})

    found_external = False
    found_away = False
    forbidden_values = []

    for cell_key, cell_data in cells.items():
        # G column cells: G2 through G26 (rows 2-26)
        if cell_key.startswith("G"):
            row_part = cell_key[1:]
            if row_part.isdigit():
                row_num = int(row_part)
                if 2 <= row_num <= 26:
                    value = cell_data.get("value", "")
                    if value == "Contractor":
                        forbidden_values.append(f"{cell_key} still has 'Contractor'")
                    if value == "On Leave":
                        forbidden_values.append(f"{cell_key} still has 'On Leave'")
                    if value == "External":
                        found_external = True
                    if value == "Away":
                        found_away = True

    if forbidden_values:
        errors.append("Found cells that were not updated: " + ", ".join(forbidden_values))
    if not found_external:
        errors.append("No cell in G column contains 'External'")
    if not found_away:
        errors.append("No cell in G column contains 'Away'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
