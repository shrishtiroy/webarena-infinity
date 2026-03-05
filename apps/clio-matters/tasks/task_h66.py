import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Fitzgerald medical malpractice case
    matter = next(
        (m for m in state.get("matters", [])
         if "fitzgerald" in m.get("description", "").lower()
         and ("misdiagnosis" in m.get("description", "").lower()
              or "medical" in m.get("description", "").lower()
              or "st. mary" in m.get("description", "").lower())),
        None,
    )
    if matter is None:
        return False, "Fitzgerald medical malpractice case not found."

    cf = matter.get("customFields", {})

    # Check Court Case Number (cf_1)
    if cf.get("cf_1") != "SF-2025-MM-7734":
        errors.append(
            f"Court Case Number is '{cf.get('cf_1')}', expected 'SF-2025-MM-7734'."
        )

    # Check Judge Assigned (cf_7)
    if cf.get("cf_7") != "Hon. Richard Alvarez":
        errors.append(
            f"Judge Assigned is '{cf.get('cf_7')}', expected 'Hon. Richard Alvarez'."
        )

    # Check Insurance Company (cf_4)
    if cf.get("cf_4") != "Kaiser Permanente":
        errors.append(
            f"Insurance Company is '{cf.get('cf_4')}', expected 'Kaiser Permanente'."
        )

    # Check Policy Limit (cf_5) - currency field, accept number or string
    policy_limit = cf.get("cf_5")
    if policy_limit is None:
        errors.append("Policy Limit not set.")
    else:
        try:
            val = float(str(policy_limit).replace(",", "").replace("$", ""))
            if abs(val - 1000000) > 1000:
                errors.append(f"Policy Limit is {policy_limit}, expected $1,000,000.")
        except (ValueError, TypeError):
            errors.append(f"Policy Limit is '{policy_limit}', expected $1,000,000.")

    if errors:
        return False, (
            f"Fitzgerald case custom fields not set correctly. " + " | ".join(errors)
        )

    return True, (
        "All four custom fields correctly set on Fitzgerald case: "
        "Court Case Number SF-2025-MM-7734, Judge Hon. Richard Alvarez, "
        "Insurance Kaiser Permanente, Policy Limit $1,000,000."
    )
