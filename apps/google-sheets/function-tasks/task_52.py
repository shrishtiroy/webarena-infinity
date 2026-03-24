import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    a2 = sheet["cells"].get("A2")
    b2 = sheet["cells"].get("B2")
    c2 = sheet["cells"].get("C2")
    if (a2 and a2.get("value") == "SKU-001" and
        (b2 is None or b2.get("value") is None) and
        c2 and c2.get("value") == "Laptop Pro 15"):
        return True, "Column inserted after A. C2 now has 'Laptop Pro 15'."
    msg = f"A2={a2.get('value') if a2 else None}, B2={b2.get('value') if b2 else None}, C2={c2.get('value') if c2 else None}"
    return False, f"Unexpected state. {msg}"
