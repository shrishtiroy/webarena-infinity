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

    # Sum settlement expenses
    expenses = rodriguez.get("settlement", {}).get("expenses", [])
    total_expenses = sum(e.get("amount", 0) for e in expenses)
    if total_expenses == 0:
        return False, "No settlement expenses found on Rodriguez case."

    # Find the damage
    damage = next(
        (d for d in rodriguez.get("damages", [])
         if "travel" in (d.get("description") or "").lower()
         and "out" in (d.get("description") or "").lower()),
        None,
    )
    if not damage:
        return False, "Damage for 'Out-of-pocket travel expenses' not found."

    errors = []
    if damage.get("type") != "Out-of-Pocket Expenses":
        errors.append(f"Damage type is '{damage.get('type')}', expected 'Out-of-Pocket Expenses'.")
    if damage.get("amount") != total_expenses:
        errors.append(
            f"Damage amount is {damage.get('amount')}, expected {total_expenses} "
            f"(sum of settlement expenses)."
        )

    if errors:
        return False, " ".join(errors)

    return True, f"Damage added with amount ${total_expenses} matching settlement expenses total."
