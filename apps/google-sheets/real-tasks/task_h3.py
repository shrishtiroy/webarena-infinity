import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    sheets = state.get("sheets", [])
    sheet_names = [s.get("name", "") for s in sheets]

    # Check 1: sheets[0].name == "Stock Management"
    if len(sheets) == 0:
        return False, "No sheets found in state."
    if sheets[0].get("name", "") != "Stock Management":
        errors.append(f"First sheet should be 'Stock Management', got '{sheets[0].get('name', '')}'")

    # Check 2: "Revenue Data" exists somewhere
    if "Revenue Data" not in sheet_names:
        errors.append(f"No sheet named 'Revenue Data' found. Sheet names: {sheet_names}")

    # Check 3: "Team Directory" exists somewhere
    if "Team Directory" not in sheet_names:
        errors.append(f"No sheet named 'Team Directory' found. Sheet names: {sheet_names}")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
