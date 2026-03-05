import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Count open matters per practice area
    pa_counts = Counter()
    for m in state.get("matters", []):
        if m.get("status") == "open":
            pa_id = m.get("practiceAreaId")
            if pa_id:
                pa_counts[pa_id] += 1

    if not pa_counts:
        return False, "No open matters found."

    top_pa_id = pa_counts.most_common(1)[0][0]
    top_count = pa_counts[top_pa_id]

    # Find this practice area
    top_pa = next(
        (pa for pa in state.get("practiceAreas", []) if pa["id"] == top_pa_id),
        None
    )
    if top_pa is None:
        return False, f"Practice area {top_pa_id} not found."

    # Check for Appeal stage at the end
    stages = top_pa.get("stages", [])
    stage_names = [s.get("name", "").lower() for s in stages]

    has_appeal = any("appeal" in sn for sn in stage_names)
    if not has_appeal:
        errors.append(
            f"No 'Appeal' stage found in {top_pa.get('name')} ({top_pa_id}), "
            f"which has the most open matters ({top_count}). "
            f"Current stages: {[s.get('name') for s in stages]}."
        )

    if errors:
        return False, " | ".join(errors)

    return True, (
        f"'Appeal' stage added to {top_pa.get('name')} ({top_pa_id}), "
        f"which has the most open matters ({top_count}). "
        f"Stages: {[s.get('name') for s in stages]}."
    )
