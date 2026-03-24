import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    a2 = sheet["cells"].get("A2")
    a3 = sheet["cells"].get("A3")
    if (a2 is None or a2.get("value") is None) and a3 and a3.get("value") == "SKU-001":
        return True, "Row inserted after row 1. A3 now has 'SKU-001'."
    msg = f"A2={a2.get('value') if a2 else None}, A3={a3.get('value') if a3 else None}"
    return False, f"Unexpected state after insert. {msg}"
