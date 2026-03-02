import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []
    settlements = state.get("settlements", {})

    # Doyle scaffolding matter
    doyle = next(
        (m for m in state.get("matters", [])
         if "doyle" in m.get("description", "").lower()
         and "scaffolding" in m.get("description", "").lower()),
        None
    )
    # Mills motorcycle matter
    mills = next(
        (m for m in state.get("matters", [])
         if "mills" in m.get("description", "").lower()
         and ("rodriguez" in m.get("description", "").lower()
              or "motorcycle" in m.get("description", "").lower())),
        None
    )

    if doyle is None:
        errors.append("Could not find the Doyle scaffolding fall matter.")
    if mills is None:
        errors.append("Could not find the Mills motorcycle collision matter.")

    for matter, name in [(doyle, "Doyle scaffolding"), (mills, "Mills motorcycle")]:
        if matter is None:
            continue
        mid = matter["id"]
        settlement = settlements.get(mid, {})
        balances = settlement.get("outstandingBalances", [])

        has_balance = any(
            abs(float(ob.get("originalAmount", ob.get("balanceOwing", 0))) - 5000) < 1000
            for ob in balances
        )
        if not has_balance:
            amounts = [ob.get("originalAmount", ob.get("balanceOwing")) for ob in balances]
            errors.append(
                f"{name} ({mid}): no ~$5,000 outstanding balance found. "
                f"Balance amounts: {amounts}."
            )

    if errors:
        return False, "Outstanding balances not added correctly. " + " | ".join(errors)

    return True, (
        "Both Doyle scaffolding and Mills motorcycle cases have "
        "$5,000 outstanding balances from Pacific Physical Therapy Center."
    )
