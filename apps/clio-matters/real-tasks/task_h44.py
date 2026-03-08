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

    # Seed state flags (before swap):
    # NM_Hospital_Bill.pdf: lien=True, outstanding=False
    # CPTC_Bill_Full.pdf: lien=False, outstanding=True
    # AIA_Invoice_Aug.pdf: lien=False, outstanding=True
    expected = {
        "NM_Hospital_Bill.pdf": {"balanceIsLien": False, "balanceIsOutstanding": True},
        "CPTC_Bill_Full.pdf": {"balanceIsLien": True, "balanceIsOutstanding": False},
        "AIA_Invoice_Aug.pdf": {"balanceIsLien": True, "balanceIsOutstanding": False},
    }

    errors = []
    found = set()
    for p in rodriguez.get("medicalProviders", []):
        for b in p.get("medicalBills", []):
            fname = b.get("fileName")
            if fname in expected:
                found.add(fname)
                exp = expected[fname]
                if b.get("balanceIsLien") != exp["balanceIsLien"]:
                    errors.append(
                        f"{fname}: balanceIsLien is {b.get('balanceIsLien')}, "
                        f"expected {exp['balanceIsLien']}."
                    )
                if b.get("balanceIsOutstanding") != exp["balanceIsOutstanding"]:
                    errors.append(
                        f"{fname}: balanceIsOutstanding is {b.get('balanceIsOutstanding')}, "
                        f"expected {exp['balanceIsOutstanding']}."
                    )

    missing = set(expected.keys()) - found
    if missing:
        errors.append(f"Bills not found: {missing}.")

    if errors:
        return False, " ".join(errors)

    return True, "Lien and outstanding flags swapped on all Rodriguez medical bills."
