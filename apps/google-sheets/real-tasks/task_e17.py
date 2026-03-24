import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a named range 'TotalRevenue' pointing to Sales!G42 exists."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    named_ranges = state.get("namedRanges", {})

    if "TotalRevenue" not in named_ranges:
        return False, f"Named range 'TotalRevenue' not found. Existing named ranges: {list(named_ranges.keys())}"

    value = named_ranges["TotalRevenue"]
    if value == "Sales!G42":
        return True, "Named range 'TotalRevenue' correctly points to 'Sales!G42'."

    return False, f"Named range 'TotalRevenue' exists but points to '{value}' instead of 'Sales!G42'."
