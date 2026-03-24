#!/usr/bin/env python3
"""
Sanity check for Google Sheets function-test tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_function.py                     # All tasks, sequential
    python3 sanity_check_function.py --workers N          # N parallel environments
    python3 sanity_check_function.py --task-id task_5     # Single task
    python3 sanity_check_function.py --port 9000          # Custom base port
"""
import argparse
import functools
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "function-tasks.json"

# JS snippet to evaluate data.js and emit the seed state as JSON
_SEED_STATE_JS = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);
const state = getSeedData();
process.stdout.write(JSON.stringify(state));
"""


# -- helpers ------------------------------------------------------------------

def find_sheet(state, name):
    """Find a sheet by name. Returns (index, sheet)."""
    for i, s in enumerate(state["sheets"]):
        if s["name"] == name:
            return i, s
    raise ValueError(f"Sheet '{name}' not found")


def col_to_index(col):
    """Convert column letter(s) to 1-based index. A=1, B=2, ..., Z=26."""
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - 64)
    return idx


def index_to_col(idx):
    """Convert 1-based index to column letter(s)."""
    s = ''
    while idx > 0:
        rem = (idx - 1) % 26
        s = chr(65 + rem) + s
        idx = (idx - 1) // 26
    return s


def parse_addr(addr):
    """Parse 'A1' into ('A', 1)."""
    m = re.match(r'^([A-Z]+)(\d+)$', addr)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def shift_cells_delete_row(cells, row):
    """Delete a row from cells dict, shifting rows above down."""
    new_cells = {}
    for addr, cell in cells.items():
        col, r = parse_addr(addr)
        if col is None:
            continue
        if r == row:
            continue
        if r > row:
            new_cells[f"{col}{r - 1}"] = cell
        else:
            new_cells[addr] = cell
    return new_cells


def shift_cells_insert_row(cells, after_row):
    """Insert a row after after_row, shifting rows below down."""
    new_cells = {}
    for addr, cell in cells.items():
        col, r = parse_addr(addr)
        if col is None:
            new_cells[addr] = cell
            continue
        if r > after_row:
            new_cells[f"{col}{r + 1}"] = cell
        else:
            new_cells[addr] = cell
    return new_cells


def shift_cells_delete_col(cells, col_letter):
    """Delete a column from cells dict, shifting columns to the right left."""
    col_idx = col_to_index(col_letter)
    new_cells = {}
    for addr, cell in cells.items():
        col, r = parse_addr(addr)
        if col is None:
            continue
        ci = col_to_index(col)
        if ci == col_idx:
            continue
        if ci > col_idx:
            new_cells[f"{index_to_col(ci - 1)}{r}"] = cell
        else:
            new_cells[addr] = cell
    return new_cells


def shift_cells_insert_col(cells, after_col_letter):
    """Insert a column after after_col_letter, shifting columns to the right."""
    after_idx = col_to_index(after_col_letter)
    new_cells = {}
    for addr, cell in cells.items():
        col, r = parse_addr(addr)
        if col is None:
            new_cells[addr] = cell
            continue
        ci = col_to_index(col)
        if ci > after_idx:
            new_cells[f"{index_to_col(ci + 1)}{r}"] = cell
        else:
            new_cells[addr] = cell
    return new_cells


def sort_sheet_by_col(sheet, sort_col, order="asc"):
    """Sort sheet data rows (2+) by a column, preserving row 1 header."""
    cells = sheet["cells"]
    # Find max row and max col
    max_row = 0
    max_col_idx = 0
    for addr in cells:
        col, r = parse_addr(addr)
        if col is None:
            continue
        if r > max_row:
            max_row = r
        ci = col_to_index(col)
        if ci > max_col_idx:
            max_col_idx = ci

    # Collect data rows (2 to max_row)
    rows = []
    for r in range(2, max_row + 1):
        row_data = {}
        for c in range(1, max_col_idx + 1):
            cl = index_to_col(c)
            addr = f"{cl}{r}"
            if addr in cells:
                row_data[cl] = deepcopy(cells[addr])
        sort_val = cells.get(f"{sort_col}{r}", {}).get("value")
        rows.append({"data": row_data, "sort_val": sort_val})

    # Sort (nulls always go to end regardless of direction)
    def compare(a, b):
        av = a["sort_val"]
        bv = b["sort_val"]
        if av is None and bv is None:
            return 0
        if av is None:
            return 1
        if bv is None:
            return -1
        if isinstance(av, (int, float)) and isinstance(bv, (int, float)):
            cmp = (av > bv) - (av < bv)
        else:
            sa, sb = str(av).lower(), str(bv).lower()
            cmp = (sa > sb) - (sa < sb)
        return cmp if order == "asc" else -cmp

    rows.sort(key=functools.cmp_to_key(compare))

    # Clear old data rows
    for r in range(2, max_row + 1):
        for c in range(1, max_col_idx + 1):
            addr = f"{index_to_col(c)}{r}"
            if addr in cells:
                del cells[addr]

    # Write sorted rows back
    for i, row in enumerate(rows):
        r = i + 2
        for col_letter, cell_data in row["data"].items():
            cells[f"{col_letter}{r}"] = cell_data


# -- solve functions ----------------------------------------------------------

# Cell Editing (tasks 1-8)

def solve_task_1(state):
    """Type 'Grand Total' into cell A43 on Sales sheet."""
    state["sheets"][0]["cells"]["A43"] = {"value": "Grand Total", "formula": None, "format": {}}


def solve_task_2(state):
    """Enter =SUM(D2:D26) in cell D27 of Employees sheet."""
    # Calculate the sum of all salaries
    sheet = state["sheets"][1]
    total = 0
    for r in range(2, 27):
        cell = sheet["cells"].get(f"D{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            total += cell["value"]
    sheet["cells"]["D27"] = {"value": total, "formula": "=SUM(D2:D26)", "format": {}}


def solve_task_3(state):
    """Change Employees G6 from 'On Leave' to 'Active'."""
    state["sheets"][1]["cells"]["G6"]["value"] = "Active"


def solve_task_4(state):
    """Update Inventory D30 (Wireless Charger Pad stock) from 0 to 500."""
    state["sheets"][2]["cells"]["D30"]["value"] = 500


def solve_task_5(state):
    """Enter =MAX(E2:E41) in cell E43 of Sales sheet."""
    sheet = state["sheets"][0]
    max_val = None
    for r in range(2, 42):
        cell = sheet["cells"].get(f"E{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            if max_val is None or cell["value"] > max_val:
                max_val = cell["value"]
    sheet["cells"]["E43"] = {"value": max_val, "formula": "=MAX(E2:E41)", "format": {}}


def solve_task_6(state):
    """Clear contents of cell H2 on Sales sheet."""
    if "H2" in state["sheets"][0]["cells"]:
        del state["sheets"][0]["cells"]["H2"]


def solve_task_7(state):
    """Enter =MIN(D2:D26) in cell D29 of Employees sheet."""
    sheet = state["sheets"][1]
    min_val = None
    for r in range(2, 27):
        cell = sheet["cells"].get(f"D{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            if min_val is None or cell["value"] < min_val:
                min_val = cell["value"]
    sheet["cells"]["D29"] = {"value": min_val, "formula": "=MIN(D2:D26)", "format": {}}


def solve_task_8(state):
    """Type 'Notes' into cell H1 of Employees sheet."""
    state["sheets"][1]["cells"]["H1"] = {"value": "Notes", "formula": None, "format": {}}


# Cell Formatting (tasks 9-20)

def solve_task_9(state):
    """Make cell A2 of Sales sheet bold."""
    cell = state["sheets"][0]["cells"]["A2"]
    cell["format"]["bold"] = True


def solve_task_10(state):
    """Make cell B3 of Employees sheet italic."""
    # B3 = row 3 Employees = Sofia Martinez's department
    cell = state["sheets"][1]["cells"]["B3"]
    cell.setdefault("format", {})["italic"] = True


def solve_task_11(state):
    """Underline cell C2 of Inventory sheet."""
    cell = state["sheets"][2]["cells"]["C2"]
    cell.setdefault("format", {})["underline"] = True


def solve_task_12(state):
    """Strikethrough cell B30 of Inventory sheet."""
    cell = state["sheets"][2]["cells"]["B30"]
    cell.setdefault("format", {})["strikethrough"] = True


def solve_task_13(state):
    """Set font color of Sales A1 to #ff0000."""
    cell = state["sheets"][0]["cells"]["A1"]
    cell["format"]["fontColor"] = "#ff0000"


def solve_task_14(state):
    """Set background color of Employees G6 to #ffff00."""
    cell = state["sheets"][1]["cells"]["G6"]
    cell.setdefault("format", {})["backgroundColor"] = "#ffff00"


def solve_task_15(state):
    """Right-align Sales D42."""
    cell = state["sheets"][0]["cells"]["D42"]
    cell["format"]["horizontalAlign"] = "right"


def solve_task_16(state):
    """Set number format of Sales E2 to 'number'."""
    cell = state["sheets"][0]["cells"]["E2"]
    cell.setdefault("format", {})["numberFormat"] = "number"


def solve_task_17(state):
    """Set number format of Employees D2 to 'percentage'."""
    cell = state["sheets"][1]["cells"]["D2"]
    cell["format"]["numberFormat"] = "percentage"


def solve_task_18(state):
    """Set decimal places of Sales F2 to 0."""
    cell = state["sheets"][0]["cells"]["F2"]
    cell["format"]["decimalPlaces"] = 0


def solve_task_19(state):
    """Center-align Inventory A1."""
    cell = state["sheets"][2]["cells"]["A1"]
    cell["format"]["horizontalAlign"] = "center"


def solve_task_20(state):
    """Set background color of Employees G2 to #90ee90."""
    cell = state["sheets"][1]["cells"]["G2"]
    cell.setdefault("format", {})["backgroundColor"] = "#90ee90"


# Sheet Management (tasks 21-28)

def solve_task_21(state):
    """Add a new blank sheet."""
    state["sheets"].append({
        "name": "Sheet4",
        "cells": {},
        "columnWidths": {},
        "rowHeights": {},
        "frozenRows": 0,
        "frozenCols": 0,
        "mergedCells": [],
        "conditionalFormats": [],
        "filters": {},
        "filterMode": False,
        "charts": []
    })
    state["activeSheet"] = 3


def solve_task_22(state):
    """Rename 'Sales' to 'Sales Report'."""
    state["sheets"][0]["name"] = "Sales Report"


def solve_task_23(state):
    """Duplicate 'Employees' sheet."""
    copy = deepcopy(state["sheets"][1])
    copy["name"] = "Employees (Copy)"
    state["sheets"].insert(2, copy)
    state["activeSheet"] = 2


def solve_task_24(state):
    """Delete 'Inventory' sheet."""
    state["sheets"].pop(2)
    if state["activeSheet"] >= len(state["sheets"]):
        state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_25(state):
    """Add a new sheet named 'Budget'."""
    state["sheets"].append({
        "name": "Budget",
        "cells": {},
        "columnWidths": {},
        "rowHeights": {},
        "frozenRows": 0,
        "frozenCols": 0,
        "mergedCells": [],
        "conditionalFormats": [],
        "filters": {},
        "filterMode": False,
        "charts": []
    })
    state["activeSheet"] = 3


def solve_task_26(state):
    """Move 'Inventory' (index 2) to index 0."""
    sheet = state["sheets"].pop(2)
    state["sheets"].insert(0, sheet)
    # If active was Sales (0), it shifts to 1
    state["activeSheet"] = 0


def solve_task_27(state):
    """Rename 'Inventory' to 'Stock Levels'."""
    state["sheets"][2]["name"] = "Stock Levels"


def solve_task_28(state):
    """Switch active sheet to Employees (index 1)."""
    state["activeSheet"] = 1


# Named Ranges (tasks 29-31)

def solve_task_29(state):
    """Create named range 'SalesTotal' -> 'Sales!G42'."""
    state["namedRanges"]["SalesTotal"] = "Sales!G42"


def solve_task_30(state):
    """Create named range 'EmployeeSalaries' -> 'Employees!D2:D26'."""
    state["namedRanges"]["EmployeeSalaries"] = "Employees!D2:D26"


def solve_task_31(state):
    """Create named range 'LowStockItems' -> 'Inventory!D2:D31'."""
    state["namedRanges"]["LowStockItems"] = "Inventory!D2:D31"


# Conditional Formatting (tasks 32-37)

def solve_task_32(state):
    """Add CF rule on Inventory D2:D31: greater_than 100, bg #c6efce."""
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "greater_than",
        "value": "100",
        "value2": "",
        "backgroundColor": "#c6efce"
    })


def solve_task_33(state):
    """Add CF rule on Inventory D2:D31: less_than 20, bg #ffc7ce."""
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "less_than",
        "value": "20",
        "value2": "",
        "backgroundColor": "#ffc7ce"
    })


def solve_task_34(state):
    """Add CF rule on Employees G2:G26: text_contains 'On Leave', bg #ffff00."""
    state["sheets"][1]["conditionalFormats"].append({
        "range": "G2:G26",
        "type": "text_contains",
        "value": "On Leave",
        "value2": "",
        "backgroundColor": "#ffff00"
    })


def solve_task_35(state):
    """Add CF rule on Sales G2:G41: greater_than 5000, bg #c6efce."""
    state["sheets"][0]["conditionalFormats"].append({
        "range": "G2:G41",
        "type": "greater_than",
        "value": "5000",
        "value2": "",
        "backgroundColor": "#c6efce"
    })


def solve_task_36(state):
    """Add CF rule on Employees D2:D26: greater_than 150000, bg #c6efce, text #006100."""
    state["sheets"][1]["conditionalFormats"].append({
        "range": "D2:D26",
        "type": "greater_than",
        "value": "150000",
        "value2": "",
        "backgroundColor": "#c6efce",
        "fontColor": "#006100"
    })


def solve_task_37(state):
    """Add CF rule on Inventory D2:D31: equal_to 0, bg #ff0000."""
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "equal_to",
        "value": "0",
        "value2": "",
        "backgroundColor": "#ff0000"
    })


# Charts (tasks 38-42)

def solve_task_38(state):
    """Create bar chart on Sales with range E1:E41 titled 'Sales Quantities'."""
    state["sheets"][0]["charts"].append({
        "id": "chart-sanity-38",
        "type": "bar",
        "dataRange": "E1:E41",
        "title": "Sales Quantities",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_39(state):
    """Create pie chart on Inventory with range C1:D31 titled 'Stock by Category'."""
    state["sheets"][2]["charts"].append({
        "id": "chart-sanity-39",
        "type": "pie",
        "dataRange": "C1:D31",
        "title": "Stock by Category",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_40(state):
    """Create line chart on Sales with range A1:G5 titled 'January Sales'."""
    state["sheets"][0]["charts"].append({
        "id": "chart-sanity-40",
        "type": "line",
        "dataRange": "A1:G5",
        "title": "January Sales",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_41(state):
    """Create scatter chart on Sales with range E1:F41 titled 'Price vs Quantity'."""
    state["sheets"][0]["charts"].append({
        "id": "chart-sanity-41",
        "type": "scatter",
        "dataRange": "E1:F41",
        "title": "Price vs Quantity",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_42(state):
    """Create horizontal bar chart on Employees with range A1:D26."""
    state["sheets"][1]["charts"].append({
        "id": "chart-sanity-42",
        "type": "horizontal_bar",
        "dataRange": "A1:D26",
        "title": "Employee Salaries",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


# Sorting (tasks 43-45)

def solve_task_43(state):
    """Sort Sales by column E (Quantity) descending."""
    sort_sheet_by_col(state["sheets"][0], "E", "desc")


def solve_task_44(state):
    """Sort Employees by column D (Salary) ascending."""
    sort_sheet_by_col(state["sheets"][1], "D", "asc")


def solve_task_45(state):
    """Sort Inventory by column D (Stock) ascending."""
    sort_sheet_by_col(state["sheets"][2], "D", "asc")


# Freeze (tasks 46-48)

def solve_task_46(state):
    """Freeze first row on Sales sheet."""
    state["sheets"][0]["frozenRows"] = 1


def solve_task_47(state):
    """Freeze first 2 columns on Employees sheet."""
    state["sheets"][1]["frozenCols"] = 2


def solve_task_48(state):
    """Freeze first 3 rows on Inventory sheet."""
    state["sheets"][2]["frozenRows"] = 3


# Insert/Delete (tasks 49-52)

def solve_task_49(state):
    """Delete row 2 from Sales sheet."""
    sheet = state["sheets"][0]
    sheet["cells"] = shift_cells_delete_row(sheet["cells"], 2)


def solve_task_50(state):
    """Insert row after row 1 in Inventory sheet."""
    sheet = state["sheets"][2]
    sheet["cells"] = shift_cells_insert_row(sheet["cells"], 1)


def solve_task_51(state):
    """Delete column H from Sales sheet."""
    sheet = state["sheets"][0]
    sheet["cells"] = shift_cells_delete_col(sheet["cells"], "H")


def solve_task_52(state):
    """Insert column after A in Inventory sheet."""
    sheet = state["sheets"][2]
    sheet["cells"] = shift_cells_insert_col(sheet["cells"], "A")


# Find and Replace (tasks 53-54)

def solve_task_53(state):
    """Replace all 'North' with 'Northern' in Sales sheet."""
    sheet = state["sheets"][0]
    for addr, cell in sheet["cells"].items():
        if cell and cell.get("value") is not None and not cell.get("formula"):
            val = str(cell["value"])
            if "North" in val:
                cell["value"] = val.replace("North", "Northern")


def solve_task_54(state):
    """Replace all 'Active' with 'Current' in Employees sheet."""
    sheet = state["sheets"][1]
    for addr, cell in sheet["cells"].items():
        if cell and cell.get("value") is not None and not cell.get("formula"):
            val = str(cell["value"])
            if "Active" in val:
                cell["value"] = val.replace("Active", "Current")


# Merge Cells (tasks 55-56)

def solve_task_55(state):
    """Merge cells A44:D44 on Sales sheet."""
    state["sheets"][0]["mergedCells"].append("A44:D44")


def solve_task_56(state):
    """Merge cells A28:C28 on Employees sheet."""
    state["sheets"][1]["mergedCells"].append("A28:C28")


# Data Validation (task 57)

def solve_task_57(state):
    """Set data validation on Employees G2 - dropdown list."""
    cell = state["sheets"][1]["cells"]["G2"]
    cell["validation"] = {
        "type": "list",
        "values": "Active,On Leave,Contractor,Terminated"
    }


# Filter (tasks 58-59)

def solve_task_58(state):
    """Enable filter mode on Sales sheet."""
    state["sheets"][0]["filterMode"] = True


def solve_task_59(state):
    """Set filter on Sales column D to hide 'West'."""
    state["sheets"][0]["filters"]["D"] = {
        "type": "values",
        "hiddenValues": ["West"]
    }


# Borders (task 60)

def solve_task_60(state):
    """Apply all borders (solid black) to Sales A1."""
    cell = state["sheets"][0]["cells"]["A1"]
    border = "1px solid #000000"
    cell["format"]["borderTop"] = border
    cell["format"]["borderBottom"] = border
    cell["format"]["borderLeft"] = border
    cell["format"]["borderRight"] = border


# -- solver registry ----------------------------------------------------------

SOLVERS = {f"task_{i}": globals()[f"solve_task_{i}"] for i in range(1, 61)}


# -- server management -------------------------------------------------------

def generate_seed_state():
    """Use Node.js to evaluate data.js and produce the seed state JSON."""
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate seed state:\n{result.stderr}")
    return json.loads(result.stdout)


def seed_server(server_url, seed_state):
    """PUT the seed state to the server to establish the baseline."""
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def find_free_port(start=9000):
    """Find a free port starting from `start`."""
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start+200}")


def start_server(port):
    """Start the server on the given port."""
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            return proc
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2)
    proc.kill()
    raise RuntimeError(f"Server failed to start on port {port}")


def stop_server(proc):
    """Stop the server process."""
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# -- task runner --------------------------------------------------------------

def load_tasks():
    """Load task definitions from function-tasks.json."""
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    """Dynamically load a verifier module."""
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url, seed_state):
    """Reset -> solve -> verify for a single task."""
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. PUT seed state to reset
        resp = requests.put(
            f"{server_url}/api/state",
            json=deepcopy(seed_state),
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        # 2. Read back state
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply solve
        solver(state)

        # 4. Write solved state
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run verifier
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
    """Run all tasks sequentially on a single server."""
    proc = start_server(port)
    server_url = f"http://localhost:{port}"
    results = []
    try:
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url, seed_state)
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")
    finally:
        stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    """Run tasks in parallel across multiple server instances."""
    results = []

    def worker_fn(task, port):
        proc = start_server(port)
        server_url = f"http://localhost:{port}"
        try:
            seed_server(server_url, seed_state)
            return run_single_task(task, server_url, seed_state)
        finally:
            stop_server(proc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for i, task in enumerate(tasks):
            port = base_port + i
            future = executor.submit(worker_fn, task, port)
            futures[future] = task["id"]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")

    return results


# -- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Google Sheets function-task sanity check")
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"Task '{args.task_id}' not found.")
            sys.exit(1)

    print("Generating seed state from JS data...")
    seed_state = generate_seed_state()
    print(f"Running {len(tasks)} task(s)...\n")

    if args.workers <= 1:
        port = find_free_port(args.port)
        results = run_tasks_sequential(tasks, port, seed_state)
    else:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [tid for tid, p, _ in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
