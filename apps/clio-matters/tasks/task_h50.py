import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Known seed: open PI matters at Demand (stage_1_3)
    demand_matter_ids = ["matter_1", "matter_6", "matter_13", "matter_24", "matter_114"]

    settlements = state.get("settlements", {})

    for mid in demand_matter_ids:
        m = next((m for m in state.get("matters", []) if m["id"] == mid), None)
        if m is None:
            errors.append(f"{mid} not found in matters.")
            continue

        settlement = settlements.get(mid, {})
        liens = settlement.get("nonMedicalLiens", [])

        # Check for $10,000 lien from State Farm
        has_lien = any(
            abs(float(l.get("amount", 0)) - 10000) < 2000
            for l in liens
        )
        if not has_lien:
            lien_amounts = [l.get("amount") for l in liens]
            errors.append(
                f"{m.get('description', mid)}: no ~$10,000 lien found. "
                f"Lien amounts: {lien_amounts}."
            )

    if errors:
        return False, "Not all PI Demand matters have the $10,000 State Farm lien. " + " | ".join(errors)

    return True, (
        f"All {len(demand_matter_ids)} open PI Demand matters have "
        f"$10,000 State Farm liens in their settlements."
    )
