import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    rodriguez = next(
        (m for m in state.get("matters", [])
         if "Rodriguez" in (m.get("description") or "") and "Premier Auto" in (m.get("description") or "")),
        None,
    )
    if not rodriguez:
        return False, "Rodriguez matter not found."

    # Seed recoveries: Lakeside $175,000 -> $350,000; Premier $85,000 -> $170,000
    # Seed legal fees: rate 33.33 -> 38.33 for both
    expected_recoveries = {"Lakeside": 350000, "Premier": 170000}
    expected_rate = 38.33

    errors = []
    recoveries = rodriguez.get("settlement", {}).get("recoveries", [])
    for r in recoveries:
        contact = next(
            (c for c in state.get("contacts", []) if c["id"] == r.get("sourceContactId")),
            None,
        )
        if contact:
            name = contact.get("lastName") or ""
            for key, expected_amt in expected_recoveries.items():
                if key in name:
                    if r.get("amount") != expected_amt:
                        errors.append(
                            f"{name} recovery: amount is {r.get('amount')}, expected {expected_amt}."
                        )
                    break

    legal_fees = rodriguez.get("settlement", {}).get("legalFees", [])
    for f in legal_fees:
        if abs(f.get("rate", 0) - expected_rate) > 0.01:
            errors.append(
                f"Legal fee (recovery {f.get('recoveryId')}): rate is {f.get('rate')}%, "
                f"expected {expected_rate}%."
            )

    if errors:
        return False, " ".join(errors)

    return True, "Rodriguez recoveries doubled, legal fee rates increased by 5 percentage points."
