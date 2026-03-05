import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settlements = state.get("settlements", {})
    matter_3_settlement = settlements.get("matter_3", {})
    recoveries = matter_3_settlement.get("recoveries", [])

    for recovery in recoveries:
        source_name = recovery.get("sourceName", "")
        recovery_id = recovery.get("id", "")
        if "ABC Insurance" in source_name or recovery_id == "rec_1":
            return False, f"Recovery from 'ABC Insurance Co.' (id: {recovery_id}) still exists in matter_3 settlements."

    return True, "Recovery from 'ABC Insurance Co.' has been successfully deleted from matter_3 settlements."
