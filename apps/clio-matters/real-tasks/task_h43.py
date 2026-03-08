import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = None
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        if "Rodriguez" in desc and "Premier Auto" in desc:
            rodriguez = m
            break
    if not rodriguez:
        return False, "Rodriguez matter not found."

    # Find the rehabilitation provider (description contains "rehab")
    rehab_provider = None
    for p in rodriguez.get("medicalProviders", []):
        desc = (p.get("description") or "").lower()
        if "rehab" in desc:
            rehab_provider = p
            break
    if not rehab_provider:
        return False, "Rehabilitation provider not found on Rodriguez case."

    bills = rehab_provider.get("medicalBills", [])
    if not bills:
        return False, "Rehabilitation provider has no medical bills."

    bill = bills[0]
    comments = bill.get("comments", [])
    expected_text = "Pending insurance adjuster review"
    has_comment = any(c.get("text") == expected_text for c in comments)

    if not has_comment:
        return False, (
            f"Comment '{expected_text}' not found on bill '{bill.get('fileName')}' "
            f"of rehabilitation provider."
        )

    return True, "Comment added to rehabilitation provider's medical bill."
