import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Set a filter on the Sales sheet to hide all sales from the West region."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Sales sheet is at index 0
    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found."

    sales = sheets[0]
    filters = sales.get("filters", {})

    if not filters:
        return False, "No filters found on the Sales sheet."

    # Region column is D
    if "D" not in filters:
        return False, f"No filter set on column D (Region). Found filters on columns: {list(filters.keys())}."

    d_filter = filters["D"]
    hidden_values = d_filter.get("hiddenValues", [])

    if "West" not in hidden_values:
        return False, f"Filter on column D does not hide 'West'. Hidden values: {hidden_values}."

    return True, f"Filter on column D hides 'West'. Hidden values: {hidden_values}."
