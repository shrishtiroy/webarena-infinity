import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # In seed data:
    # Contingency open matters (should now be hourly): Rodriguez, Foster, Cruz, Harris, Kowalski
    # Hourly open matters (should now be flat_rate): TechNova, Okafor, Mendez, Morales
    # Flat_rate open matters (unchanged): Singh, Baker
    expected = {
        "Rodriguez": "hourly",
        "Foster": "hourly",
        "Cruz": "hourly",
        "Harris": "hourly",
        "Kowalski": "hourly",
        "TechNova": "flat_rate",
        "Okafor": "flat_rate",
        "Mendez": "flat_rate",
        "Morales": "flat_rate",
        "Singh": "flat_rate",
        "Baker": "flat_rate",
    }

    errors = []
    matched = 0
    for m in state.get("matters", []):
        if m.get("status") != "Open":
            continue
        desc = m.get("description") or ""
        billing = m.get("billingPreference", {}).get("billingMethod")
        for name, exp in expected.items():
            if name in desc:
                if billing != exp:
                    errors.append(
                        f"'{desc}': billing is '{billing}', expected '{exp}'."
                    )
                else:
                    matched += 1
                break

    if matched < 9:
        errors.append(f"Only {matched}/11 open matters have correct billing method.")

    if errors:
        return False, " ".join(errors)

    return True, "Billing methods swapped: contingency to hourly, hourly to flat_rate."
