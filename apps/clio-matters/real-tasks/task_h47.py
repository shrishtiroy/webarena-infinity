import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Seed-data open contingency matters and their original rates:
    # Rodriguez: 33.33, Foster: 40, Cruz: 33.33, Harris: 33.33, Kowalski: 20
    # After +5: 38.33, 45, 38.33, 38.33, 25
    expected = [
        ("Rodriguez", 38.33),
        ("Foster", 45),
        ("Cruz", 38.33),
        ("Harris", 38.33),
        ("Kowalski", 25),
    ]

    errors = []
    matched = 0
    for m in state.get("matters", []):
        bp = m.get("billingPreference", {})
        if m.get("status") != "Open" or bp.get("billingMethod") != "contingency":
            continue
        desc = m.get("description", "")
        for name, exp_rate in expected:
            if name in desc:
                matched += 1
                rate = bp.get("contingencyRate")
                if rate is None or abs(rate - exp_rate) > 0.02:
                    errors.append(
                        f"{desc}: contingency rate is {rate}, expected {exp_rate}."
                    )
                break

    if matched < 5:
        errors.append(f"Only {matched} open contingency matters found, expected 5.")

    if errors:
        return False, " ".join(errors)

    return True, "All 5 open contingency matters had rates increased by 5 percentage points."
