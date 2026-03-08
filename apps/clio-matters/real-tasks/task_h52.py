import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find PI practice area
    pi_id = None
    for pa in state.get("practiceAreas", []):
        if pa.get("name") == "Personal Injury":
            pi_id = pa.get("id")
            break
    if not pi_id:
        return False, "Personal Injury practice area not found."

    # To find the case that WAS the smallest before the task was run,
    # subtract the newly-added damages from totals for comparison.
    target_types = {"Future Medical Costs", "Loss of Earning Capacity"}
    best_matter = None
    best_total = float("inf")
    for m in state.get("matters", []):
        if m.get("practiceAreaId") == pi_id and m.get("status") == "Open":
            damages = m.get("damages", [])
            # Exclude the two target damage types so we get the pre-task baseline
            baseline = sum(
                d.get("amount", 0) for d in damages
                if d.get("type") not in target_types
            )
            if baseline < best_total:
                best_total = baseline
                best_matter = m

    if not best_matter:
        return False, "No open PI matter found."

    damages = best_matter.get("damages", [])

    # Check for Future Medical Costs $20,000
    future_med = [
        d for d in damages
        if d.get("type") == "Future Medical Costs" and d.get("amount") == 20000
    ]
    if not future_med:
        return False, (
            f"No 'Future Medical Costs' damage for $20,000 found on "
            f"'{best_matter.get('description')}' (smallest baseline damages: ${best_total:,.0f})."
        )

    # Check for Loss of Earning Capacity $15,000
    earning_cap = [
        d for d in damages
        if d.get("type") == "Loss of Earning Capacity" and d.get("amount") == 15000
    ]
    if not earning_cap:
        return False, (
            f"No 'Loss of Earning Capacity' damage for $15,000 found on "
            f"'{best_matter.get('description')}'."
        )

    return True, (
        f"Two damages added to '{best_matter.get('description')}' "
        f"(PI case with smallest damages)."
    )
