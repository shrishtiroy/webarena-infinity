import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # In seed data, open matters with zero trust AND zero WIP:
    # Singh (mat_007): WIP=0, trust=0
    # Baker (mat_010): WIP=0, trust=0
    should_be_closed = ["Singh", "Baker"]
    should_remain_open = [
        "Rodriguez", "Foster", "TechNova", "Okafor",
        "Cruz", "Mendez", "Harris", "Kowalski", "Morales",
    ]

    errors = []
    for m in state.get("matters", []):
        desc = m.get("description") or ""
        status = m.get("status")

        for name in should_be_closed:
            if name in desc:
                if status != "Closed":
                    errors.append(
                        f"'{desc}' should be Closed (had zero trust and zero WIP), "
                        f"but is '{status}'."
                    )
                break

        for name in should_remain_open:
            if name in desc:
                # These should NOT have been closed by this task
                # (they were either already closed, pending, or had nonzero funds)
                break

    # Verify at least 2 matters were closed
    closed_count = sum(
        1 for m in state.get("matters", [])
        if any(n in (m.get("description") or "") for n in should_be_closed)
        and m.get("status") == "Closed"
    )
    if closed_count < 2:
        errors.append(f"Expected 2 matters closed, found {closed_count}.")

    if errors:
        return False, " ".join(errors)

    return True, "Singh and Baker closed (both had zero trust funds and zero WIP)."
