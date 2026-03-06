import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    src = next((q for q in state["quotes"] if q["number"] == "QU-0024"), None)
    if not src:
        return False, "Original quote QU-0024 not found."

    copies = [q for q in state["quotes"]
              if q["contactId"] == src["contactId"]
              and q["status"] == "draft"
              and q["number"] != "QU-0024"
              and abs(q["total"] - src["total"]) < 0.01]

    if not copies:
        return False, "No draft copy of QU-0024 found for Atlas Engineering."

    return True, f"Quote QU-0024 duplicated as {copies[0]['number']}."
