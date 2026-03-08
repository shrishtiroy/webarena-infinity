import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Count open matters per responsible attorney
    counts = {}
    for m in state.get("matters", []):
        if m.get("status") == "Open":
            atty = m.get("responsibleAttorneyId")
            if atty:
                counts[atty] = counts.get(atty, 0) + 1

    if not counts:
        return False, "No open matters with responsible attorneys found."

    best_atty_id = max(counts, key=counts.get)

    # Find Criminal Defense - Misdemeanor template
    tmpl = None
    for t in state.get("matterTemplates", []):
        name = t.get("name") or ""
        if "Criminal Defense" in name and "Misdemeanor" in name:
            tmpl = t
            break
    if not tmpl:
        return False, "Criminal Defense - Misdemeanor template not found."

    errors = []
    if tmpl.get("responsibleAttorneyId") != best_atty_id:
        errors.append(
            f"Template responsible attorney is '{tmpl.get('responsibleAttorneyId')}', "
            f"expected '{best_atty_id}' (attorney with most open matters: {counts[best_atty_id]})."
        )
    if tmpl.get("billingMethod") != "contingency":
        errors.append(
            f"Template billing method is '{tmpl.get('billingMethod')}', expected 'contingency'."
        )
    rate = tmpl.get("contingencyRate")
    if rate is None or abs(rate - 30) > 0.02:
        errors.append(f"Template contingency rate is {rate}, expected 30.")

    if errors:
        return False, " ".join(errors)

    return True, "Criminal Defense template updated with busiest attorney and contingency at 30%."
