import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find the duplicated matter (should contain "Supplemental claim")
    duplicate = next(
        (m for m in state.get("matters", [])
         if "supplemental claim" in m.get("description", "").lower()
         or ("patterson" in m.get("description", "").lower()
             and "supplemental" in m.get("description", "").lower())),
        None,
    )
    if duplicate is None:
        # Fallback: look for a Patterson matter with "(Copy)" in description
        duplicate = next(
            (m for m in state.get("matters", [])
             if "patterson" in m.get("description", "").lower()
             and "(copy)" in m.get("description", "").lower()),
            None,
        )
    if duplicate is None:
        return False, "Duplicated Patterson matter with 'Supplemental claim' description not found."

    # Check responsible attorney is Diana Reyes (user_3)
    if duplicate.get("responsibleAttorneyId") != "user_3":
        errors.append(
            f"Responsible attorney is '{duplicate.get('responsibleAttorneyId')}', "
            f"expected 'user_3' (Diana Reyes)."
        )

    # Check billing method is hourly
    method = duplicate.get("billingMethod", duplicate.get("billing", {}).get("method"))
    if method != "hourly":
        errors.append(f"Billing method is '{method}', expected 'hourly'.")

    # Check budget
    budget = duplicate.get("billing", {}).get("budget", 0)
    if abs(budget - 25000) > 2000:
        errors.append(f"Budget is ${budget:,.0f}, expected $25,000.")

    # Verify original Patterson matter still exists
    original = next(
        (m for m in state.get("matters", [])
         if "patterson" in m.get("description", "").lower()
         and "metro transit" in m.get("description", "").lower()
         and m["id"] != duplicate["id"]
         and "supplemental" not in m.get("description", "").lower()),
        None,
    )
    if original is None:
        errors.append("Original Patterson bus accident matter not found.")

    if errors:
        return False, "Patterson duplicate not set up correctly. " + " | ".join(errors)

    return True, (
        f"Patterson matter duplicated and modified correctly: "
        f"description updated to Supplemental claim, attorney Diana Reyes, "
        f"hourly billing, $25,000 budget."
    )
