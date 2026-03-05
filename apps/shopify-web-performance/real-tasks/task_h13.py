import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    alerts = settings.get("performanceAlerts", {})
    errors = []

    if settings.get("deviceFilter") != "mobile":
        errors.append(f"Device filter is '{settings.get('deviceFilter')}', expected 'mobile'.")
    if settings.get("dateRange") != "today":
        errors.append(f"Date range is '{settings.get('dateRange')}', expected 'today'.")
    if settings.get("comparisonEnabled") is not False:
        errors.append(f"Comparison enabled is {settings.get('comparisonEnabled')}, expected False.")
    if alerts.get("degradationPercent") != 10:
        errors.append(f"Degradation percent is {alerts.get('degradationPercent')}, expected 10.")

    if errors:
        return False, " ".join(errors)

    return True, "Dashboard configured for daily mobile review: mobile filter, today range, comparison disabled, degradation at 10%."
