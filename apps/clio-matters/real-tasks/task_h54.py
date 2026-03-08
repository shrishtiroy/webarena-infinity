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

    # Find provider with earliest treatment start date
    best_provider = None
    earliest_date = None
    for p in rodriguez.get("medicalProviders", []):
        first_date = p.get("treatmentFirstDate")
        if first_date and (earliest_date is None or first_date < earliest_date):
            earliest_date = first_date
            best_provider = p

    if not best_provider:
        return False, "No medical providers with treatment dates found."

    bills = best_provider.get("medicalBills", [])
    if not bills:
        return False, (
            f"Provider with earliest treatment (started {earliest_date}) has no bills."
        )

    bill = bills[0]
    errors = []

    if bill.get("billAmount") != 50000:
        errors.append(
            f"Bill amount is {bill.get('billAmount')}, expected 50000."
        )
    if bill.get("adjustment") != 8000:
        errors.append(
            f"Bill adjustment is {bill.get('adjustment')}, expected 8000."
        )

    if errors:
        return False, (
            f"On bill '{bill.get('fileName')}' (earliest provider, "
            f"started {earliest_date}): " + " ".join(errors)
        )

    return True, (
        f"Bill updated on earliest-treatment provider (started {earliest_date}): "
        f"amount=$50,000, adjustment=$8,000."
    )
