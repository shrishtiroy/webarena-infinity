import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find CD practice area
    cd_pa_id = "pa_3"

    # Count CD matters per attorney
    cd_matters = [
        m for m in state.get("matters", [])
        if m.get("practiceAreaId") == cd_pa_id
    ]

    attorney_counts = Counter()
    for m in cd_matters:
        atty = m.get("responsibleAttorneyId")
        if atty:
            attorney_counts[atty] += 1

    if not attorney_counts:
        return False, "No Criminal Defense matters found."

    top_attorney = attorney_counts.most_common(1)[0][0]
    # Should be user_8 (Robert Jackson) with the most CD matters

    # Find new matter for Marcus Thompson (contact_9) with CD practice area
    thompson_cd_matters = [
        m for m in state.get("matters", [])
        if m.get("clientId") == "contact_9"
        and m.get("practiceAreaId") == cd_pa_id
    ]

    # Filter to only new matters (not in original seed)
    known_thompson_cd = {"matter_44", "matter_50"}
    new_thompson_cd = [
        m for m in thompson_cd_matters
        if m.get("id") not in known_thompson_cd
    ]

    if not new_thompson_cd:
        errors.append(
            "No new Criminal Defense matter found for client Marcus Thompson (contact_9)."
        )
    else:
        new_matter = new_thompson_cd[0]

        # Check responsible attorney is the top CD attorney
        if new_matter.get("responsibleAttorneyId") != top_attorney:
            errors.append(
                f"New matter's attorney is '{new_matter.get('responsibleAttorneyId')}', "
                f"expected '{top_attorney}' (the attorney with the most CD matters)."
            )

        # Check flat rate billing at $8,000
        if new_matter.get("billingMethod") != "flat_rate":
            errors.append(
                f"New matter billing method is '{new_matter.get('billingMethod')}', "
                f"expected 'flat_rate'."
            )

        billing = new_matter.get("billing", {})
        flat_rate = billing.get("flatRate")
        if flat_rate is None:
            errors.append("New matter has no flatRate set.")
        else:
            amount = flat_rate.get("amount", 0)
            if abs(float(amount) - 8000) > 500:
                errors.append(f"Flat rate amount is ${amount}, expected ~$8,000.")

    if errors:
        return False, "New CD matter for Thompson not created correctly. " + " | ".join(errors)

    users = {u["id"]: u["name"] for u in state.get("users", [])}
    atty_name = users.get(top_attorney, top_attorney)
    return True, (
        f"New Criminal Defense matter created for Marcus Thompson with "
        f"{atty_name} ({top_attorney}) as responsible attorney and flat rate $8,000."
    )
