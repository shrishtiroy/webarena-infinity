import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Calculate total budget per practice area (open matters only)
    budget_by_pa = {}
    for m in state.get("matters", []):
        if m.get("status") != "open":
            continue
        pa_id = m.get("practiceAreaId")
        budget = m.get("billing", {}).get("budget", 0)
        budget_by_pa[pa_id] = budget_by_pa.get(pa_id, 0) + budget

    if not budget_by_pa:
        return False, "No open matters with budgets found."

    top_pa_id = max(budget_by_pa, key=budget_by_pa.get)
    top_budget = budget_by_pa[top_pa_id]

    pa = next((p for p in state.get("practiceAreas", []) if p["id"] == top_pa_id), None)
    if pa is None:
        return False, f"Practice area {top_pa_id} not found."

    # Check for Financial Review stage
    stage_names = [s["name"] for s in pa.get("stages", [])]
    has_stage = any("financial review" == s.lower() for s in stage_names)

    if not has_stage:
        errors.append(
            f"Stage 'Financial Review' not found in {pa['name']} ({top_pa_id}, "
            f"highest budget ${top_budget:,.0f}). Stages: {stage_names}."
        )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"Correctly identified {pa['name']} ({top_pa_id}) as having the highest "
        f"total open-matter budget (${top_budget:,.0f}) and added Financial Review stage."
    )
