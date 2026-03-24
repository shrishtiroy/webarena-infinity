import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    named_ranges = state.get("namedRanges", {})

    expected = {
        "Salaries": "Employees!D2:D26",
        "Departments": "Employees!B2:B26",
        "StartDates": "Employees!E2:E26",
    }

    for name, expected_value in expected.items():
        actual = named_ranges.get(name)
        if actual is None:
            errors.append(f"Named range '{name}' not found")
        elif actual != expected_value:
            errors.append(f"Named range '{name}' is '{actual}', expected '{expected_value}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
