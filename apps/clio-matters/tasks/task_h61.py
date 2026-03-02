import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find matter with most total billable hours
    time_entries = state.get("timeEntries", [])
    hours_by_matter = {}
    for te in time_entries:
        mid = te.get("matterId")
        hours_by_matter[mid] = hours_by_matter.get(mid, 0) + float(te.get("hours", 0))

    if not hours_by_matter:
        return False, "No time entries found in state."

    top_matter_id = max(hours_by_matter, key=hours_by_matter.get)
    top_hours = hours_by_matter[top_matter_id]

    matter = next((m for m in state.get("matters", []) if m["id"] == top_matter_id), None)
    if matter is None:
        return False, f"Matter {top_matter_id} not found."

    # Check status is pending
    if matter.get("status") != "pending":
        errors.append(
            f"{matter.get('description')} status is '{matter.get('status')}', expected 'pending'."
        )

    # Check Court Case Number custom field
    cf_value = matter.get("customFields", {}).get("cf_1", "")
    if cf_value != "HIGH-PRIORITY-2026":
        errors.append(
            f"Court Case Number is '{cf_value}', expected 'HIGH-PRIORITY-2026'."
        )

    if errors:
        return False, (
            f"Matter with most billable hours ({top_matter_id}, {top_hours:.1f}hrs) "
            f"not updated correctly. " + " | ".join(errors)
        )

    return True, (
        f"Correctly identified {matter.get('description')} ({top_matter_id}, "
        f"{top_hours:.1f}hrs) as having the most billable hours. "
        f"Status set to pending and Court Case Number set to HIGH-PRIORITY-2026."
    )
