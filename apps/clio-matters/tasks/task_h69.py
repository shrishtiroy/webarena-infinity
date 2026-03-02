import requests
from collections import Counter


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find attorney with most originating attorney assignments on open matters
    counts = Counter()
    for m in state.get("matters", []):
        if m.get("status") == "open":
            orig = m.get("originatingAttorneyId")
            if orig:
                counts[orig] += 1

    if not counts:
        return False, "No open matters with originating attorneys found."

    top_atty = counts.most_common(1)[0][0]

    # Find new Corporate matter for Redwood Financial Services
    # Exclude known existing matter_70 (SEC compliance audit) which also has contact_38 + pa_5
    new_matter = next(
        (m for m in state.get("matters", [])
         if m.get("practiceAreaId") == "pa_5"
         and m.get("clientId") == "contact_38"
         and m["id"] != "matter_70"),
        None,
    )
    if new_matter is None:
        # Fallback: search by description
        new_matter = next(
            (m for m in state.get("matters", [])
             if m["id"] != "matter_70"
             and (m.get("clientId") == "contact_38"
                  or ("redwood" in m.get("description", "").lower()
                      and "financial" in m.get("description", "").lower()))),
            None,
        )

    if new_matter is None:
        return False, (
            f"No Corporate matter found for Redwood Financial Services. "
            f"Top originating attorney is {top_atty}."
        )

    # Check responsible attorney matches top originating attorney
    if new_matter.get("responsibleAttorneyId") != top_atty:
        errors.append(
            f"Responsible attorney is '{new_matter.get('responsibleAttorneyId')}', "
            f"expected '{top_atty}' (top originating attorney)."
        )

    # Check originating attorney matches too
    if new_matter.get("originatingAttorneyId") != top_atty:
        errors.append(
            f"Originating attorney is '{new_matter.get('originatingAttorneyId')}', "
            f"expected '{top_atty}'."
        )

    # Check hourly billing
    method = new_matter.get("billingMethod", new_matter.get("billing", {}).get("method"))
    if method != "hourly":
        errors.append(f"Billing method is '{method}', expected 'hourly'.")

    # Check budget
    budget = new_matter.get("billing", {}).get("budget", 0)
    if abs(budget - 40000) > 3000:
        errors.append(f"Budget is ${budget:,.0f}, expected $40,000.")

    if errors:
        return False, (
            f"New Corporate matter for Redwood Financial not set up correctly. "
            + " | ".join(errors)
        )

    return True, (
        f"Correctly identified {top_atty} as top originating attorney and created "
        f"Corporate matter for Redwood Financial Services with correct settings."
    )
