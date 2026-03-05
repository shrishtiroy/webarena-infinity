import requests
from collections import defaultdict


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find top 3 PI matters by total damages
    pi_ids = {m["id"] for m in state.get("matters", []) if m.get("practiceAreaId") == "pa_1"}
    totals = defaultdict(float)
    for d in state.get("damages", []):
        mid = d.get("matterId")
        if mid in pi_ids:
            totals[mid] += float(d.get("amount", 0))

    if len(totals) < 3:
        return False, f"Only {len(totals)} PI matters have damages, need at least 3."

    # Sort by total damages descending, take top 3
    sorted_matters = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    top_3 = [mid for mid, _ in sorted_matters[:3]]

    # Check each has a $10,000 non-medical lien from State Farm
    for mid in top_3:
        settlement = state.get("settlements", {}).get(mid, {})
        liens = settlement.get("nonMedicalLiens", [])
        has_sf_lien = any(
            abs(float(l.get("amount", 0)) - 10000) < 2000
            and (l.get("holderContactId") == "contact_58"
                 or "state farm" in l.get("description", "").lower())
            for l in liens
        )
        if not has_sf_lien:
            matter = next((m for m in state.get("matters", []) if m["id"] == mid), None)
            desc = matter.get("description", mid) if matter else mid
            total_dmg = totals[mid]
            lien_list = [(l.get("amount"), l.get("description")) for l in liens]
            errors.append(
                f"{desc} (${total_dmg:,.0f} in damages) missing $10,000 State Farm lien. "
                f"Liens: {lien_list}."
            )

    if errors:
        return False, "Top 3 PI damage matters not all updated. " + " | ".join(errors)

    return True, (
        f"$10,000 State Farm lien correctly added to all three top PI damage matters: "
        f"{', '.join(top_3)}."
    )
