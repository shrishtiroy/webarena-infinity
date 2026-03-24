import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 3:
        errors.append(f"Expected at least 3 sheets, found {len(sheets)}")

    for i, sheet in enumerate(sheets):
        name = sheet.get("name", f"Sheet {i}")
        frozen_rows = sheet.get("frozenRows", 0)
        if frozen_rows < 1:
            errors.append(f"Sheet '{name}' has frozenRows={frozen_rows}, expected >= 1")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
