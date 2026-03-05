import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the two open PI matters at Litigation stage
    # In seed: matter_4 (Washington, 2024-04-20) and matter_7 (Okafor, 2024-07-22)
    # After task: matter_4 is earliest -> $15K outstanding balance
    #            matter_7 is later -> $10K non-medical lien

    # matter_4 (Washington) - opened earliest - should have outstanding balance ~$15K
    matter_4 = next(
        (m for m in state.get("matters", [])
         if "washington" in m.get("description", "").lower()
         and "pacific steel" in m.get("description", "").lower()),
        None,
    )
    if matter_4 is None:
        return False, "Washington v. Pacific Steel matter not found."

    settlement_4 = state.get("settlements", {}).get(matter_4["id"], {})
    balances = settlement_4.get("outstandingBalances", [])
    has_balance = any(
        abs(float(b.get("balanceOwing", b.get("originalAmount", 0))) - 15000) < 2000
        for b in balances
    )
    if not has_balance:
        bal_amounts = [b.get("balanceOwing", b.get("originalAmount")) for b in balances]
        errors.append(
            f"Washington case (opened earliest) missing $15,000 outstanding balance. "
            f"Balances: {bal_amounts}."
        )

    # matter_7 (Okafor) - opened later - should have non-medical lien ~$10K
    matter_7 = next(
        (m for m in state.get("matters", [])
         if "okafor" in m.get("description", "").lower()
         and ("homecomfort" in m.get("description", "").lower()
              or "burn" in m.get("description", "").lower()
              or "heater" in m.get("description", "").lower())),
        None,
    )
    if matter_7 is None:
        return False, "Okafor burn injury matter not found."

    settlement_7 = state.get("settlements", {}).get(matter_7["id"], {})
    liens = settlement_7.get("nonMedicalLiens", [])
    has_lien = any(
        abs(float(l.get("amount", 0)) - 10000) < 2000
        for l in liens
    )
    if not has_lien:
        lien_amounts = [l.get("amount") for l in liens]
        errors.append(
            f"Okafor case (opened later) missing $10,000 non-medical lien. "
            f"Liens: {lien_amounts}."
        )

    if errors:
        return False, (
            "Two Litigation-stage PI matters not updated correctly. " + " | ".join(errors)
        )

    return True, (
        "Both PI Litigation matters updated correctly: Washington (earliest) got "
        "$15,000 outstanding balance, Okafor (later) got $10,000 non-medical lien."
    )
