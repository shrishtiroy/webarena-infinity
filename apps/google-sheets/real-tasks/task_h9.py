import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    sheets = state.get("sheets", [])
    sheet_names = [s.get("name", "") for s in sheets]

    # Check 1: No sheet named "Inventory"
    if "Inventory" in sheet_names:
        errors.append("Sheet 'Inventory' should have been deleted but still exists")

    # Check 2: No sheet named "Sales"
    if "Sales" in sheet_names:
        errors.append("Sheet 'Sales' should have been renamed but still exists with original name")

    # Check 3: Sheet named "Main Data" exists
    if "Main Data" not in sheet_names:
        errors.append(f"No sheet named 'Main Data' found. Sheet names: {sheet_names}")

    # Check 4: Sheet named "Analysis" exists
    if "Analysis" not in sheet_names:
        errors.append(f"No sheet named 'Analysis' found. Sheet names: {sheet_names}")

    # Check 5: Sheet named "Charts" exists
    if "Charts" not in sheet_names:
        errors.append(f"No sheet named 'Charts' found. Sheet names: {sheet_names}")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
