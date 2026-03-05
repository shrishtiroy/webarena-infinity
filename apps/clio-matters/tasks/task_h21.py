import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find PI practice area
    pi_pa = next(
        (pa for pa in state.get("practiceAreas", [])
         if pa.get("id") == "pa_1" or "personal injury" in pa.get("name", "").lower()),
        None
    )
    if pi_pa is None:
        return False, "Could not find Personal Injury practice area."

    pi_pa_id = pi_pa["id"]

    # Count medical providers per PI matter
    pi_matter_ids = {
        m["id"] for m in state.get("matters", [])
        if m.get("practiceAreaId") == pi_pa_id
    }

    provider_counts = Counter()
    for mp in state.get("medicalProviders", []):
        mid = mp.get("matterId")
        if mid in pi_matter_ids:
            provider_counts[mid] += 1

    if not provider_counts:
        return False, "No medical providers found for any PI matter."

    # The matter with the most providers (should be matter_1 with 3)
    top_matter_id = provider_counts.most_common(1)[0][0]
    top_count = provider_counts[top_matter_id]

    # Check that a general damage for long-term disability was added
    damages = state.get("damages", [])
    matter_damages = [d for d in damages if d.get("matterId") == top_matter_id]

    disability_damage = None
    for d in matter_damages:
        if d.get("type") == "general" and abs(float(d.get("amount", 0)) - 50000) < 5000:
            disability_damage = d
            break

    if disability_damage is None:
        existing_amounts = [(d.get("name"), d.get("amount"), d.get("type")) for d in matter_damages]
        errors.append(
            f"No general damage with amount close to $50,000 found on matter {top_matter_id} "
            f"(the PI matter with the most medical providers, {top_count} providers). "
            f"Existing damages: {existing_amounts}."
        )

    if errors:
        return False, " | ".join(errors)

    matter = next((m for m in state["matters"] if m["id"] == top_matter_id), None)
    desc = matter.get("description", "") if matter else ""
    return True, (
        f"General damage ~$50,000 added to {top_matter_id} ('{desc}'), "
        f"which has the most medical providers ({top_count})."
    )
