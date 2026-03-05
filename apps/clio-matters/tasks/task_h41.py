import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find PI matter with highest total damages
    pi_matters = [m for m in state.get("matters", []) if m.get("practiceAreaId") == "pa_1"]
    damages = state.get("damages", [])

    damage_totals = {}
    for d in damages:
        mid = d.get("matterId")
        if any(m["id"] == mid for m in pi_matters):
            damage_totals[mid] = damage_totals.get(mid, 0) + float(d.get("amount", 0))

    if not damage_totals:
        return False, "No damages found for any Personal Injury matter."

    top_matter_id = max(damage_totals, key=damage_totals.get)
    top_total = damage_totals[top_matter_id]

    top_matter = next((m for m in pi_matters if m["id"] == top_matter_id), None)
    if top_matter is None:
        return False, f"Matter {top_matter_id} not found."

    # Check settlement
    settlements = state.get("settlements", {})
    settlement = settlements.get(top_matter_id, {})

    if not settlement:
        return False, (
            f"No settlement found for {top_matter.get('description')} ({top_matter_id}), "
            f"which has the highest PI damages total (${top_total:,.0f})."
        )

    # Check recovery ~$300,000
    recoveries = settlement.get("recoveries", [])
    has_recovery = any(
        abs(float(r.get("amount", 0)) - 300000) < 30000
        for r in recoveries
    )
    if not has_recovery:
        amounts = [r.get("amount") for r in recoveries]
        errors.append(f"No recovery ~$300,000 found. Recovery amounts: {amounts}.")

    # Check 33.33% legal fee
    legal_fees = settlement.get("legalFees", [])
    has_fee = any(
        abs(float(lf.get("percentage", lf.get("rate", 0))) - 33.33) < 2
        for lf in legal_fees
    )
    if not has_fee:
        pcts = [lf.get("percentage", lf.get("rate")) for lf in legal_fees]
        errors.append(f"No legal fee ~33.33% found. Fee percentages: {pcts}.")

    if errors:
        return False, (
            f"Settlement for {top_matter.get('description')} ({top_matter_id}, "
            f"highest PI damages ${top_total:,.0f}) not set up correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"Settlement correctly set up on {top_matter.get('description')} ({top_matter_id}), "
        f"which has the highest PI damages total (${top_total:,.0f}): "
        f"~$300,000 recovery and ~33.33% contingency fee."
    )
