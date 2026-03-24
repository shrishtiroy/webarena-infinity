import requests
from collections import defaultdict


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])

    # Find Sales sheet to compute region totals
    sales = None
    for s in sheets:
        if s.get("name", "") in ("Sales", "Revenue Data", "Revenue"):
            sales = s
            break
    if sales is None and len(sheets) > 0:
        sales = sheets[0]
    if sales is None:
        return False, "Sales sheet not found."

    s_cells = sales.get("cells", {})
    region_totals = defaultdict(float)
    for r in range(2, 42):
        d_cell = s_cells.get(f"D{r}")
        g_cell = s_cells.get(f"G{r}")
        if d_cell and g_cell and isinstance(g_cell.get("value"), (int, float)):
            region = str(d_cell.get("value", ""))
            region_totals[region] += g_cell["value"]

    if not region_totals:
        return False, "No region/revenue data found on Sales sheet."

    # Find Region Analysis sheet
    ra = None
    for s in sheets:
        if s.get("name", "").strip() == "Region Analysis":
            ra = s
            break
    if ra is None:
        return False, f"No sheet named 'Region Analysis' found. Sheets: {[s['name'] for s in sheets]}"

    ra_cells = ra.get("cells", {})

    # Check headers
    a1 = ra_cells.get("A1", {})
    if str(a1.get("value", "")).strip() != "Region":
        errors.append(f"A1 should be 'Region', got '{a1.get('value', '')}'")
    if not a1.get("format", {}).get("bold"):
        errors.append("A1 should be bold")

    b1 = ra_cells.get("B1", {})
    if str(b1.get("value", "")).strip() != "Total Revenue":
        errors.append(f"B1 should be 'Total Revenue', got '{b1.get('value', '')}'")
    if not b1.get("format", {}).get("bold"):
        errors.append("B1 should be bold")

    # Check regions listed alphabetically
    sorted_regions = sorted(region_totals.keys())
    max_rev = max(region_totals.values())

    for i, region in enumerate(sorted_regions):
        row = i + 2
        a_val = str(ra_cells.get(f"A{row}", {}).get("value", "")).strip()
        if a_val != region:
            errors.append(f"A{row} should be '{region}', got '{a_val}'")

        b_cell = ra_cells.get(f"B{row}", {})
        b_val = b_cell.get("value")
        expected = region_totals[region]
        if isinstance(b_val, (int, float)):
            if abs(b_val - expected) > 0.02:
                errors.append(f"B{row} should be ~{expected:.2f}, got {b_val}")
        else:
            errors.append(f"B{row} should be numeric, got '{b_val}'")

        # Check highest revenue cell has green bg
        if abs(region_totals[region] - max_rev) < 0.01:
            bg = str(b_cell.get("format", {}).get("backgroundColor", "")).lower()
            if bg != "#c6efce":
                errors.append(f"B{row} (highest revenue) bg should be '#c6efce', got '{bg}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Region Analysis sheet created correctly."
