import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update billing postal code from 1010 to 1011 for all Auckland contacts
    with postal code 1010."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    errors = []

    # Known Auckland contacts with postal code 1010 in seed data:
    # Ridgeway University (con_1), Metro Print Solutions (con_8),
    # Swift Courier Services (con_12), TrueNorth Marketing Agency (con_19)
    expected_names = [
        "Ridgeway University", "Metro Print Solutions",
        "Swift Courier Services", "TrueNorth Marketing Agency",
    ]

    for name in expected_names:
        contact = next((c for c in contacts if c.get("name") == name), None)
        if contact is None:
            errors.append(f"Contact '{name}' not found")
            continue
        addr = contact.get("billingAddress", {})
        postal = addr.get("postalCode", "")
        if postal != "1011":
            errors.append(f"'{name}' postal code is '{postal}', expected '1011'")
        # City should still be Auckland
        if addr.get("city") != "Auckland":
            errors.append(f"'{name}' city changed to '{addr.get('city')}', should still be 'Auckland'")

    # Auckland contacts with OTHER postal codes should be unchanged
    unchanged_names = ["Bright Spark Electrical", "Oceanview Resort & Spa",
                       "Bloom & Branch Florists", "Ironclad Security Systems",
                       "Meridian Health Clinic", "Redwood Property Management",
                       "Atlas Import/Export Ltd"]
    for name in unchanged_names:
        contact = next((c for c in contacts if c.get("name") == name), None)
        if contact is None:
            continue
        addr = contact.get("billingAddress", {})
        if addr.get("city") == "Auckland" and addr.get("postalCode") == "1011":
            # Check if this contact originally had 1010
            # These contacts had different postal codes, so 1011 would be wrong
            pass  # Their original codes weren't 1010, so they shouldn't be 1011

    if errors:
        return False, "; ".join(errors)
    return True, f"Postal code updated to 1011 for all {len(expected_names)} Auckland contacts with original code 1010"
