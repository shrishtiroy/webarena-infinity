import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    merged = sheet.get("mergedCells", [])
    if "A44:D44" in merged:
        return True, "Cells A44:D44 merged on Sales sheet."
    return False, f"Merged cells: {merged}"
