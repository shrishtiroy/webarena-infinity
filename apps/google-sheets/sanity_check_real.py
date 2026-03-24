#!/usr/bin/env python3
"""
Sanity check for Google Sheets real tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_real.py                     # All tasks, sequential
    python3 sanity_check_real.py --workers N          # N parallel environments
    python3 sanity_check_real.py --task-id task_e1    # Single task
    python3 sanity_check_real.py --port 9600          # Custom base port
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
TASKS_FILE = APP_DIR / "real-tasks.json"

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
    for i, s in enumerate(state["sheets"]):
        if s["name"] == name:
            return i, s
    raise ValueError(f"Sheet '{name}' not found")


def col_to_index(col):
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - 64)
    return idx


def index_to_col(idx):
    s = ''
    while idx > 0:
        rem = (idx - 1) % 26
        s = chr(65 + rem) + s
        idx = (idx - 1) // 26
    return s


def parse_addr(addr):
    m = re.match(r'^([A-Z]+)(\d+)$', addr)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def shift_cells_delete_col(cells, col_letter):
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


def shift_cells_insert_row(cells, after_row):
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


def sort_sheet_by_col(sheet, sort_col, order="asc"):
    cells = sheet["cells"]
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

    for r in range(2, max_row + 1):
        for c in range(1, max_col_idx + 1):
            addr = f"{index_to_col(c)}{r}"
            if addr in cells:
                del cells[addr]

    for i, row in enumerate(rows):
        r = i + 2
        for col_letter, cell_data in row["data"].items():
            cells[f"{col_letter}{r}"] = cell_data


def sum_col(sheet, col, start_row, end_row):
    total = 0
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            total += cell["value"]
    return total


def avg_col(sheet, col, start_row, end_row):
    total = 0
    count = 0
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            total += cell["value"]
            count += 1
    return total / count if count > 0 else 0


def min_col(sheet, col, start_row, end_row):
    vals = []
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            vals.append(cell["value"])
    return min(vals) if vals else 0


def max_col(sheet, col, start_row, end_row):
    vals = []
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            vals.append(cell["value"])
    return max(vals) if vals else 0


def count_col(sheet, col, start_row, end_row):
    count = 0
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            count += 1
    return count


def counta_col(sheet, col, start_row, end_row):
    count = 0
    for r in range(start_row, end_row + 1):
        cell = sheet["cells"].get(f"{col}{r}")
        if cell and cell.get("value") is not None and cell.get("value") != "":
            count += 1
    return count


def find_replace(sheet, old_val, new_val):
    for addr, cell in sheet["cells"].items():
        if cell and cell.get("value") is not None and not cell.get("formula"):
            val = str(cell["value"])
            if old_val in val:
                cell["value"] = val.replace(old_val, new_val)


def create_empty_sheet(name):
    return {
        "name": name,
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
    }


# -- Easy solve functions (task_e1 - task_e20) --------------------------------

def solve_task_e1(state):
    """Update Amara Okafor's status to Active."""
    state["sheets"][1]["cells"]["G6"]["value"] = "Active"


def solve_task_e2(state):
    """Rename Sales sheet to Revenue."""
    state["sheets"][0]["name"] = "Revenue"


def solve_task_e3(state):
    """Freeze top row on Sales."""
    state["sheets"][0]["frozenRows"] = 1


def solve_task_e4(state):
    """Delete Inventory sheet."""
    state["sheets"].pop(2)
    if state["activeSheet"] >= len(state["sheets"]):
        state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_e5(state):
    """Add Summary sheet."""
    state["sheets"].append(create_empty_sheet("Summary"))
    state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_e6(state):
    """Switch to Employees sheet."""
    state["activeSheet"] = 1


def solve_task_e7(state):
    """Bold Priya Sharma's name."""
    state["sheets"][1]["cells"]["A2"]["format"]["bold"] = True


def solve_task_e8(state):
    """Right-align Totals label."""
    state["sheets"][0]["cells"]["D42"]["format"]["horizontalAlign"] = "right"


def solve_task_e9(state):
    """Clear salesperson from first sale."""
    if "H2" in state["sheets"][0]["cells"]:
        del state["sheets"][0]["cells"]["H2"]


def solve_task_e10(state):
    """Update Wireless Charger Pad stock to 50."""
    state["sheets"][2]["cells"]["D30"]["value"] = 50


def solve_task_e11(state):
    """Rename Employees to Team."""
    state["sheets"][1]["name"] = "Team"


def solve_task_e12(state):
    """Enable filter mode on Sales."""
    state["sheets"][0]["filterMode"] = True


def solve_task_e13(state):
    """Underline Laptop Pro 15 on Inventory."""
    state["sheets"][2]["cells"]["B2"].setdefault("format", {})["underline"] = True


def solve_task_e14(state):
    """Add Notes header in I1 on Sales."""
    state["sheets"][0]["cells"]["I1"] = {"value": "Notes", "formula": None, "format": {}}


def solve_task_e15(state):
    """Strikethrough Wireless Charger Pad on Inventory."""
    state["sheets"][2]["cells"]["B30"].setdefault("format", {})["strikethrough"] = True


def solve_task_e16(state):
    """Freeze first two columns on Employees."""
    state["sheets"][1]["frozenCols"] = 2


def solve_task_e17(state):
    """Create TotalRevenue named range."""
    state["namedRanges"]["TotalRevenue"] = "Sales!G42"


def solve_task_e18(state):
    """Merge A44:D44 on Sales."""
    state["sheets"][0]["mergedCells"].append("A44:D44")


def solve_task_e19(state):
    """Duplicate Sales sheet."""
    copy = deepcopy(state["sheets"][0])
    copy["name"] = "Sales (Copy)"
    state["sheets"].insert(1, copy)
    state["activeSheet"] = 1


def solve_task_e20(state):
    """Change Oliver Grant salary to 200000."""
    state["sheets"][1]["cells"]["D18"]["value"] = 200000


# -- Medium solve functions (task_m1 - task_m20) ------------------------------

def solve_task_m1(state):
    """Sum all salaries in D27 on Employees."""
    sheet = state["sheets"][1]
    total = sum_col(sheet, "D", 2, 26)
    sheet["cells"]["D27"] = {"value": total, "formula": "=SUM(D2:D26)", "format": {}}


def solve_task_m2(state):
    """Sort Inventory by stock ascending."""
    sort_sheet_by_col(state["sheets"][2], "D", "asc")


def solve_task_m3(state):
    """CF on Inventory: stock < 20, red bg."""
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "less_than",
        "value": "20",
        "value2": "",
        "backgroundColor": "#ffc7ce"
    })


def solve_task_m4(state):
    """Bar chart on Sales for Quantity."""
    state["sheets"][0]["charts"].append({
        "id": "chart-sanity-m4",
        "type": "bar",
        "dataRange": "E1:E41",
        "title": "Sales Volume",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_m5(state):
    """Replace Engineering with Product on Employees."""
    find_replace(state["sheets"][1], "Engineering", "Product")


def solve_task_m6(state):
    """Bold, italic, underline Priya Sharma's name."""
    fmt = state["sheets"][1]["cells"]["A2"]["format"]
    fmt["bold"] = True
    fmt["italic"] = True
    fmt["underline"] = True


def solve_task_m7(state):
    """Data validation dropdown on Priya Sharma's status cell."""
    cell = state["sheets"][1]["cells"]["G2"]
    cell["validation"] = {
        "type": "list",
        "values": "Active,On Leave,Contractor,Terminated"
    }


def solve_task_m8(state):
    """Duplicate Employees, rename to Employees Backup."""
    copy = deepcopy(state["sheets"][1])
    copy["name"] = "Employees Backup"
    state["sheets"].insert(2, copy)
    state["activeSheet"] = 2


def solve_task_m9(state):
    """Filter Sales to hide West region."""
    state["sheets"][0]["filterMode"] = True
    state["sheets"][0]["filters"]["D"] = {
        "type": "values",
        "hiddenValues": ["West"]
    }


def solve_task_m10(state):
    """CF on Employees: salary > 150000, green bg + dark green text."""
    state["sheets"][1]["conditionalFormats"].append({
        "range": "D2:D26",
        "type": "greater_than",
        "value": "150000",
        "value2": "",
        "backgroundColor": "#c6efce",
        "fontColor": "#006100"
    })


def solve_task_m11(state):
    """Move Inventory to first position."""
    sheet = state["sheets"].pop(2)
    state["sheets"].insert(0, sheet)
    state["activeSheet"] = 0


def solve_task_m12(state):
    """Line chart on Sales for January Sales."""
    state["sheets"][0]["charts"].append({
        "id": "chart-sanity-m12",
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


def solve_task_m13(state):
    """CF on Inventory: stock == 0, red bg."""
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "equal_to",
        "value": "0",
        "value2": "",
        "backgroundColor": "#ff0000"
    })


def solve_task_m14(state):
    """Average salary formula in D28, currency format."""
    sheet = state["sheets"][1]
    avg = avg_col(sheet, "D", 2, 26)
    sheet["cells"]["D28"] = {
        "value": avg,
        "formula": "=AVERAGE(D2:D26)",
        "format": {"numberFormat": "currency"}
    }


def solve_task_m15(state):
    """Replace North with Northern on Sales."""
    find_replace(state["sheets"][0], "North", "Northern")


def solve_task_m16(state):
    """Freeze header row and enable filter on Sales."""
    state["sheets"][0]["frozenRows"] = 1
    state["sheets"][0]["filterMode"] = True


def solve_task_m17(state):
    """Create AllSalaries and AllStock named ranges."""
    state["namedRanges"]["AllSalaries"] = "Employees!D2:D26"
    state["namedRanges"]["AllStock"] = "Inventory!D2:D31"


def solve_task_m18(state):
    """Delete Salesperson column (H) from Sales."""
    state["sheets"][0]["cells"] = shift_cells_delete_col(
        state["sheets"][0]["cells"], "H"
    )


def solve_task_m19(state):
    """Sort Inventory alphabetically by product name."""
    sort_sheet_by_col(state["sheets"][2], "B", "asc")


def solve_task_m20(state):
    """Red text + light gray bg on Sales Date header."""
    cell = state["sheets"][0]["cells"]["A1"]
    cell["format"]["fontColor"] = "#ff0000"
    cell["format"]["backgroundColor"] = "#e0e0e0"


# -- Hard solve functions (task_h1 - task_h20) --------------------------------

def solve_task_h1(state):
    """Salary summary: Total/Average/Minimum in A27-A29, formulas in D27-D29."""
    sheet = state["sheets"][1]
    total = sum_col(sheet, "D", 2, 26)
    avg = avg_col(sheet, "D", 2, 26)
    minimum = min_col(sheet, "D", 2, 26)

    sheet["cells"]["A27"] = {"value": "Total", "formula": None, "format": {"bold": True}}
    sheet["cells"]["D27"] = {"value": total, "formula": "=SUM(D2:D26)", "format": {"numberFormat": "currency"}}
    sheet["cells"]["A28"] = {"value": "Average", "formula": None, "format": {"bold": True}}
    sheet["cells"]["D28"] = {"value": avg, "formula": "=AVERAGE(D2:D26)", "format": {"numberFormat": "currency"}}
    sheet["cells"]["A29"] = {"value": "Minimum", "formula": None, "format": {"bold": True}}
    sheet["cells"]["D29"] = {"value": minimum, "formula": "=MIN(D2:D26)", "format": {"numberFormat": "currency"}}


def solve_task_h2(state):
    """Sort Employees by dept, freeze header, CF for On Leave."""
    sheet = state["sheets"][1]
    sort_sheet_by_col(sheet, "B", "asc")
    sheet["frozenRows"] = 1
    sheet["conditionalFormats"].append({
        "range": "G2:G26",
        "type": "text_contains",
        "value": "On Leave",
        "value2": "",
        "backgroundColor": "#ffff00"
    })


def solve_task_h3(state):
    """Rename all sheets, move Stock Management to first."""
    state["sheets"][0]["name"] = "Revenue Data"
    state["sheets"][1]["name"] = "Team Directory"
    state["sheets"][2]["name"] = "Stock Management"
    sheet = state["sheets"].pop(2)
    state["sheets"].insert(0, sheet)
    state["activeSheet"] = 0


def solve_task_h4(state):
    """Inventory analysis setup: freeze, filter, CF, pie chart."""
    sheet = state["sheets"][2]
    sheet["frozenRows"] = 1
    sheet["filterMode"] = True
    sheet["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "less_than",
        "value": "20",
        "value2": "",
        "backgroundColor": "#ffc7ce"
    })
    sheet["charts"].append({
        "id": "chart-sanity-h4",
        "type": "pie",
        "dataRange": "C1:D31",
        "title": "Stock Distribution",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })


def solve_task_h5(state):
    """Bold all names A2:A26, italicize all depts B2:B26."""
    sheet = state["sheets"][1]
    for r in range(2, 27):
        a_cell = sheet["cells"].get(f"A{r}")
        if a_cell:
            a_cell.setdefault("format", {})["bold"] = True
        b_cell = sheet["cells"].get(f"B{r}")
        if b_cell:
            b_cell.setdefault("format", {})["italic"] = True


def solve_task_h6(state):
    """Create Dashboard sheet with cross-sheet formulas."""
    sales_sheet = state["sheets"][0]
    emp_sheet = state["sheets"][1]
    total_rev = sum_col(sales_sheet, "G", 2, 41)
    emp_count = counta_col(emp_sheet, "A", 2, 26)

    dashboard = create_empty_sheet("Dashboard")
    dashboard["cells"]["A1"] = {"value": "Total Revenue", "formula": None, "format": {"bold": True}}
    dashboard["cells"]["B1"] = {"value": total_rev, "formula": "=SUM(Sales!G2:G41)", "format": {}}
    dashboard["cells"]["A2"] = {"value": "Employee Count", "formula": None, "format": {"bold": True}}
    dashboard["cells"]["B2"] = {"value": emp_count, "formula": "=COUNTA(Employees!A2:A26)", "format": {}}
    state["sheets"].append(dashboard)
    state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_h7(state):
    """Replace categories and sort Inventory."""
    sheet = state["sheets"][2]
    find_replace(sheet, "Accessories", "Add-ons")
    find_replace(sheet, "Peripherals", "Hardware")
    sort_sheet_by_col(sheet, "C", "asc")


def solve_task_h8(state):
    """Three CF rules on Inventory stock."""
    cf = state["sheets"][2]["conditionalFormats"]
    cf.append({
        "range": "D2:D31",
        "type": "greater_than",
        "value": "100",
        "value2": "",
        "backgroundColor": "#c6efce"
    })
    cf.append({
        "range": "D2:D31",
        "type": "less_than",
        "value": "20",
        "value2": "",
        "backgroundColor": "#ffc7ce"
    })
    cf.append({
        "range": "D2:D31",
        "type": "equal_to",
        "value": "0",
        "value2": "",
        "backgroundColor": "#ff0000"
    })


def solve_task_h9(state):
    """Delete Inventory, rename Sales to Main Data, add Analysis + Charts sheets."""
    # Delete Inventory (index 2)
    state["sheets"].pop(2)
    # Rename Sales
    state["sheets"][0]["name"] = "Main Data"
    # Add new sheets
    state["sheets"].append(create_empty_sheet("Analysis"))
    state["sheets"].append(create_empty_sheet("Charts"))
    if state["activeSheet"] >= len(state["sheets"]):
        state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_h10(state):
    """Summary rows: Count in A45/E45, Avg Price in A46/F46."""
    sheet = state["sheets"][0]
    cnt = count_col(sheet, "E", 2, 41)
    avg = avg_col(sheet, "F", 2, 41)

    sheet["cells"]["A45"] = {"value": "Count", "formula": None, "format": {"bold": True}}
    sheet["cells"]["E45"] = {"value": cnt, "formula": "=COUNT(E2:E41)", "format": {}}
    sheet["cells"]["A46"] = {"value": "Avg Price", "formula": None, "format": {"bold": True}}
    sheet["cells"]["F46"] = {"value": avg, "formula": "=AVERAGE(F2:F41)", "format": {}}


def solve_task_h11(state):
    """Freeze header row on all three sheets."""
    for sheet in state["sheets"]:
        sheet["frozenRows"] = 1


def solve_task_h12(state):
    """Replace Contractor->External, On Leave->Away on Employees."""
    sheet = state["sheets"][1]
    find_replace(sheet, "Contractor", "External")
    find_replace(sheet, "On Leave", "Away")


def solve_task_h13(state):
    """Create Low Stock Alert sheet with formatted headers."""
    sheet = create_empty_sheet("Low Stock Alert")
    header_fmt = {"bold": True, "backgroundColor": "#cfe2f3"}
    sheet["cells"]["A1"] = {"value": "Product", "formula": None, "format": dict(header_fmt)}
    sheet["cells"]["B1"] = {"value": "Current Stock", "formula": None, "format": dict(header_fmt)}
    sheet["cells"]["C1"] = {"value": "Reorder Level", "formula": None, "format": dict(header_fmt)}
    state["sheets"].append(sheet)
    state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_h14(state):
    """Two charts on Sales: bar + scatter."""
    charts = state["sheets"][0]["charts"]
    charts.append({
        "id": "chart-sanity-h14a",
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
    charts.append({
        "id": "chart-sanity-h14b",
        "type": "scatter",
        "dataRange": "E1:F41",
        "title": "Price vs Quantity",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 400},
        "size": {"width": 450, "height": 300}
    })


def solve_task_h15(state):
    """Create three named ranges for Employees."""
    state["namedRanges"]["Salaries"] = "Employees!D2:D26"
    state["namedRanges"]["Departments"] = "Employees!B2:B26"
    state["namedRanges"]["StartDates"] = "Employees!E2:E26"


def solve_task_h16(state):
    """Sort Sales by qty desc, freeze, CF on totals > 5000."""
    sheet = state["sheets"][0]
    sort_sheet_by_col(sheet, "E", "desc")
    sheet["frozenRows"] = 1
    sheet["conditionalFormats"].append({
        "range": "G2:G41",
        "type": "greater_than",
        "value": "5000",
        "value2": "",
        "backgroundColor": "#c6efce"
    })


def solve_task_h17(state):
    """SUM formula in D27 (bold+currency), CF >130000, freeze row+col."""
    sheet = state["sheets"][1]
    total = sum_col(sheet, "D", 2, 26)
    sheet["cells"]["D27"] = {
        "value": total,
        "formula": "=SUM(D2:D26)",
        "format": {"bold": True, "numberFormat": "currency"}
    }
    sheet["conditionalFormats"].append({
        "range": "D2:D26",
        "type": "greater_than",
        "value": "130000",
        "value2": "",
        "backgroundColor": "#c6efce"
    })
    sheet["frozenRows"] = 1
    sheet["frozenCols"] = 1


def solve_task_h18(state):
    """Merge A44:D44, Summary Statistics in A44 bold, formulas in E44/F44/G44."""
    sheet = state["sheets"][0]
    sheet["mergedCells"].append("A44:D44")
    sheet["cells"]["A44"] = {"value": "Summary Statistics", "formula": None, "format": {"bold": True}}
    cnt = count_col(sheet, "E", 2, 41)
    avg = avg_col(sheet, "F", 2, 41)
    mx = max_col(sheet, "G", 2, 41)
    sheet["cells"]["E44"] = {"value": cnt, "formula": "=COUNT(E2:E41)", "format": {}}
    sheet["cells"]["F44"] = {"value": avg, "formula": "=AVERAGE(F2:F41)", "format": {}}
    sheet["cells"]["G44"] = {"value": mx, "formula": "=MAX(G2:G41)", "format": {}}


def solve_task_h19(state):
    """Duplicate Employees as Salary Analysis, sort by salary desc, CF < 70000."""
    copy = deepcopy(state["sheets"][1])
    copy["name"] = "Salary Analysis"
    state["sheets"].insert(2, copy)
    sort_sheet_by_col(state["sheets"][2], "D", "desc")
    state["sheets"][2]["conditionalFormats"].append({
        "range": "D2:D26",
        "type": "less_than",
        "value": "70000",
        "value2": "",
        "backgroundColor": "#ffc7ce"
    })
    state["activeSheet"] = 2


def solve_task_h20(state):
    """Replace statuses, CF for Away, create TeamStatus named range."""
    sheet = state["sheets"][1]
    find_replace(sheet, "On Leave", "Away")
    find_replace(sheet, "Active", "Current")
    sheet["conditionalFormats"].append({
        "range": "G2:G26",
        "type": "text_contains",
        "value": "Away",
        "value2": "",
        "backgroundColor": "#ffff00"
    })
    state["namedRanges"]["TeamStatus"] = "Employees!G2:G26"


# -- Hardening round 1 solve functions (task_h21 - task_h40) ------------------

def solve_task_h21(state):
    """Create Department Summary sheet with dept counts."""
    from collections import Counter
    emp_sheet = state["sheets"][1]
    dept_counter = Counter()
    for r in range(2, 27):
        cell = emp_sheet["cells"].get(f"B{r}")
        if cell and cell.get("value"):
            dept_counter[str(cell["value"])] += 1

    ds = create_empty_sheet("Department Summary")
    for i, dept in enumerate(sorted(dept_counter.keys())):
        row = i + 1
        ds["cells"][f"A{row}"] = {"value": dept, "formula": None, "format": {"bold": True}}
        ds["cells"][f"B{row}"] = {"value": dept_counter[dept], "formula": None, "format": {}}
    state["sheets"].append(ds)
    state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_h22(state):
    """Bold+underline lowest salary employee, red bg on salary, status Under Review."""
    sheet = state["sheets"][1]
    min_sal = None
    min_row = None
    for r in range(2, 27):
        cell = sheet["cells"].get(f"D{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            if min_sal is None or cell["value"] < min_sal:
                min_sal = cell["value"]
                min_row = r

    if min_row:
        sheet["cells"][f"A{min_row}"].setdefault("format", {})["bold"] = True
        sheet["cells"][f"A{min_row}"]["format"]["underline"] = True
        sheet["cells"][f"D{min_row}"].setdefault("format", {})["backgroundColor"] = "#ffc7ce"
        sheet["cells"][f"G{min_row}"]["value"] = "Under Review"


def solve_task_h23(state):
    """Bold product names where stock < reorder, CF for zero stock."""
    sheet = state["sheets"][2]
    for r in range(2, 32):
        d_cell = sheet["cells"].get(f"D{r}")
        e_cell = sheet["cells"].get(f"E{r}")
        if d_cell and e_cell:
            stock = d_cell.get("value", 0)
            reorder = e_cell.get("value", 0)
            if isinstance(stock, (int, float)) and isinstance(reorder, (int, float)):
                if stock < reorder:
                    b_cell = sheet["cells"].get(f"B{r}")
                    if b_cell:
                        b_cell.setdefault("format", {})["bold"] = True

    sheet["conditionalFormats"].append({
        "range": "D2:D31",
        "type": "equal_to",
        "value": "0",
        "value2": "",
        "backgroundColor": "#cc0000",
        "fontColor": "#ffffff"
    })


def solve_task_h24(state):
    """Sort employees by salary desc, freeze, add rank column."""
    sheet = state["sheets"][1]
    sort_sheet_by_col(sheet, "D", "desc")
    sheet["frozenRows"] = 1
    sheet["frozenCols"] = 1
    sheet["cells"]["H1"] = {"value": "Rank", "formula": None, "format": {"bold": True}}
    for r in range(2, 27):
        sheet["cells"][f"H{r}"] = {"value": r - 1, "formula": None, "format": {}}


def solve_task_h25(state):
    """Disambiguate two Docking Station products by unit cost."""
    sheet = state["sheets"][2]
    # Docking Station USB-C: row 14, cost $95 (cheaper)
    # Docking Station TB4: row 15, cost $140 (more expensive)
    # More expensive: stock=25, bold
    sheet["cells"]["D15"]["value"] = 25
    sheet["cells"]["B15"].setdefault("format", {})["bold"] = True
    # Cheaper: italic + strikethrough
    sheet["cells"]["B14"].setdefault("format", {})["italic"] = True
    sheet["cells"]["B14"]["format"]["strikethrough"] = True


def solve_task_h26(state):
    """Add Commission formula column on Sales."""
    sheet = state["sheets"][0]
    sheet["cells"]["I1"] = {"value": "Commission", "formula": None, "format": {"bold": True}}
    total_commission = 0
    for r in range(2, 42):
        g_cell = sheet["cells"].get(f"G{r}")
        g_val = g_cell["value"] if g_cell and isinstance(g_cell.get("value"), (int, float)) else 0
        comm = g_val * 0.05
        total_commission += comm
        sheet["cells"][f"I{r}"] = {
            "value": comm,
            "formula": f"=G{r}*0.05",
            "format": {"numberFormat": "currency"}
        }
    sheet["cells"]["I42"] = {
        "value": total_commission,
        "formula": "=SUM(I2:I41)",
        "format": {"bold": True, "numberFormat": "currency"}
    }


def solve_task_h27(state):
    """Change On Leave→Returning (blue bg), Contractor→Vendor (orange bg)."""
    sheet = state["sheets"][1]
    for r in range(2, 27):
        g_cell = sheet["cells"].get(f"G{r}")
        if g_cell:
            val = g_cell.get("value", "")
            if val == "On Leave":
                g_cell["value"] = "Returning"
                g_cell.setdefault("format", {})["backgroundColor"] = "#cfe2f3"
            elif val == "Contractor":
                g_cell["value"] = "Vendor"
                g_cell.setdefault("format", {})["backgroundColor"] = "#fce5cd"


def solve_task_h28(state):
    """Find highest total salary dept, highlight its salary cells green, label in A27/B27."""
    from collections import defaultdict
    sheet = state["sheets"][1]
    dept_totals = defaultdict(float)
    dept_rows = defaultdict(list)
    for r in range(2, 27):
        dept_cell = sheet["cells"].get(f"B{r}")
        sal_cell = sheet["cells"].get(f"D{r}")
        if dept_cell and sal_cell:
            dept = str(dept_cell.get("value", ""))
            sal = sal_cell.get("value", 0)
            if isinstance(sal, (int, float)):
                dept_totals[dept] += sal
                dept_rows[dept].append(r)

    top_dept = max(dept_totals, key=dept_totals.get)
    for r in dept_rows[top_dept]:
        sheet["cells"][f"D{r}"].setdefault("format", {})["backgroundColor"] = "#c6efce"

    sheet["cells"]["A27"] = {"value": "Highest Dept", "formula": None, "format": {"bold": True}}
    sheet["cells"]["B27"] = {"value": top_dept, "formula": None, "format": {}}


def solve_task_h29(state):
    """Four CF rules on Inventory stock, named range, freeze."""
    sheet = state["sheets"][2]
    cf = sheet["conditionalFormats"]
    cf.append({"range": "D2:D31", "type": "equal_to", "value": "0", "value2": "", "backgroundColor": "#ff0000"})
    cf.append({"range": "D2:D31", "type": "between", "value": "1", "value2": "10", "backgroundColor": "#fce5cd"})
    cf.append({"range": "D2:D31", "type": "between", "value": "11", "value2": "19", "backgroundColor": "#ffff00"})
    cf.append({"range": "D2:D31", "type": "greater_than", "value": "100", "value2": "", "backgroundColor": "#c6efce"})
    state["namedRanges"]["StockLevels"] = "Inventory!D2:D31"
    sheet["frozenRows"] = 1


def solve_task_h30(state):
    """KPI Dashboard with 5 cross-sheet formula rows."""
    sales = state["sheets"][0]
    emp = state["sheets"][1]
    total_rev = sum_col(sales, "G", 2, 41)
    avg_sale = avg_col(sales, "G", 2, 41)
    max_sale = max_col(sales, "G", 2, 41)
    headcount = counta_col(emp, "A", 2, 26)
    avg_salary = avg_col(emp, "D", 2, 26)

    kpi = create_empty_sheet("KPI Dashboard")
    kpi["cells"]["A1"] = {"value": "Total Revenue", "formula": None, "format": {"bold": True}}
    kpi["cells"]["B1"] = {"value": total_rev, "formula": "=SUM(Sales!G2:G41)", "format": {"numberFormat": "currency"}}
    kpi["cells"]["A2"] = {"value": "Average Sale", "formula": None, "format": {"bold": True}}
    kpi["cells"]["B2"] = {"value": avg_sale, "formula": "=AVERAGE(Sales!G2:G41)", "format": {"numberFormat": "currency"}}
    kpi["cells"]["A3"] = {"value": "Max Sale", "formula": None, "format": {"bold": True}}
    kpi["cells"]["B3"] = {"value": max_sale, "formula": "=MAX(Sales!G2:G41)", "format": {"numberFormat": "currency"}}
    kpi["cells"]["A4"] = {"value": "Headcount", "formula": None, "format": {"bold": True}}
    kpi["cells"]["B4"] = {"value": headcount, "formula": "=COUNTA(Employees!A2:A26)", "format": {}}
    kpi["cells"]["A5"] = {"value": "Avg Salary", "formula": None, "format": {"bold": True}}
    kpi["cells"]["B5"] = {"value": avg_salary, "formula": "=AVERAGE(Employees!D2:D26)", "format": {"numberFormat": "currency"}}
    state["sheets"].append(kpi)
    state["activeSheet"] = len(state["sheets"]) - 1


def solve_task_h31(state):
    """Replace PeriphCo Supply, delete col H, sort by name, freeze."""
    sheet = state["sheets"][2]
    find_replace(sheet, "PeriphCo Supply", "PeriphCo International")
    sheet["cells"] = shift_cells_delete_col(sheet["cells"], "H")
    sort_sheet_by_col(sheet, "B", "asc")
    sheet["frozenRows"] = 1


def solve_task_h32(state):
    """Duplicate Sales as Sales Analysis, sort by total desc, freeze, bar chart."""
    copy = deepcopy(state["sheets"][0])
    copy["name"] = "Sales Analysis"
    state["sheets"].insert(1, copy)
    sort_sheet_by_col(state["sheets"][1], "G", "desc")
    state["sheets"][1]["frozenRows"] = 1
    state["sheets"][1]["charts"].append({
        "id": "chart-sanity-h32",
        "type": "bar",
        "dataRange": "G1:G41",
        "title": "Top Sales by Amount",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })
    state["activeSheet"] = 1


def solve_task_h33(state):
    """Move Employees to first, rename to Team, create Archive sheet."""
    emp = state["sheets"].pop(1)
    emp["name"] = "Team"
    state["sheets"].insert(0, emp)
    state["activeSheet"] = 0

    archive = create_empty_sheet("Archive")
    hdr_fmt = {"bold": True, "backgroundColor": "#e0e0e0"}
    archive["cells"]["A1"] = {"value": "Sheet Name", "formula": None, "format": dict(hdr_fmt)}
    archive["cells"]["B1"] = {"value": "Row Count", "formula": None, "format": dict(hdr_fmt)}
    archive["cells"]["C1"] = {"value": "Status", "formula": None, "format": dict(hdr_fmt)}
    archive["cells"]["A2"] = {"value": "Team", "formula": None, "format": {}}
    archive["cells"]["B2"] = {"value": 25, "formula": None, "format": {}}
    archive["cells"]["C2"] = {"value": "Active", "formula": None, "format": {}}
    archive["cells"]["A3"] = {"value": "Sales", "formula": None, "format": {}}
    archive["cells"]["B3"] = {"value": 40, "formula": None, "format": {}}
    archive["cells"]["C3"] = {"value": "Active", "formula": None, "format": {}}
    archive["cells"]["A4"] = {"value": "Inventory", "formula": None, "format": {}}
    archive["cells"]["B4"] = {"value": 30, "formula": None, "format": {}}
    archive["cells"]["C4"] = {"value": "Active", "formula": None, "format": {}}
    state["sheets"].append(archive)


def solve_task_h34(state):
    """Gray bg on TechDist Global supplier cells, bar chart, freeze."""
    sheet = state["sheets"][2]
    for r in range(2, 32):
        g_cell = sheet["cells"].get(f"G{r}")
        if g_cell and str(g_cell.get("value", "")) == "TechDist Global":
            g_cell.setdefault("format", {})["backgroundColor"] = "#e0e0e0"

    sheet["charts"].append({
        "id": "chart-sanity-h34",
        "type": "bar",
        "dataRange": "B1:D31",
        "title": "Stock Levels",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "showLegend": True,
        "legendPosition": "top",
        "position": {"x": 250, "y": 50},
        "size": {"width": 450, "height": 300}
    })
    sheet["frozenRows"] = 1


def solve_task_h35(state):
    """Bulk data validation + underline on status cells + named range."""
    sheet = state["sheets"][1]
    validation = {"type": "list", "values": "Active,On Leave,Contractor,Terminated,Remote"}
    for r in range(2, 27):
        cell = sheet["cells"].get(f"G{r}")
        if cell:
            cell["validation"] = dict(validation)
            cell.setdefault("format", {})["underline"] = True
    state["namedRanges"]["StatusColumn"] = "Employees!G2:G26"


def solve_task_h36(state):
    """Freeze headers + light blue bg on all 3 sheets, create named ranges."""
    header_cols = {
        0: list("ABCDEFGH"),  # Sales
        1: list("ABCDEFG"),   # Employees
        2: list("ABCDEFGH"),  # Inventory
    }
    for si, cols in header_cols.items():
        sheet = state["sheets"][si]
        sheet["frozenRows"] = 1
        for col in cols:
            cell = sheet["cells"].get(f"{col}1")
            if cell:
                cell.setdefault("format", {})["backgroundColor"] = "#cfe2f3"

    state["namedRanges"]["SalesHeaders"] = "Sales!A1:H1"
    state["namedRanges"]["EmployeeHeaders"] = "Employees!A1:G1"
    state["namedRanges"]["InventoryHeaders"] = "Inventory!A1:H1"


def solve_task_h37(state):
    """MAX/MIN formulas + labels + colored bg + currency + named range."""
    sheet = state["sheets"][1]
    mx = max_col(sheet, "D", 2, 26)
    mn = min_col(sheet, "D", 2, 26)

    sheet["cells"]["C27"] = {"value": "Highest Salary", "formula": None, "format": {"bold": True}}
    sheet["cells"]["D27"] = {
        "value": mx, "formula": "=MAX(D2:D26)",
        "format": {"backgroundColor": "#c6efce", "numberFormat": "currency"}
    }
    sheet["cells"]["C28"] = {"value": "Lowest Salary", "formula": None, "format": {"bold": True}}
    sheet["cells"]["D28"] = {
        "value": mn, "formula": "=MIN(D2:D26)",
        "format": {"backgroundColor": "#ffc7ce", "numberFormat": "currency"}
    }
    state["namedRanges"]["SalaryRange"] = "Employees!D2:D26"


def solve_task_h38(state):
    """Filter hide West, replace Wireless Mouse, blue B1 text, named range."""
    sheet = state["sheets"][0]
    sheet["filterMode"] = True
    sheet["filters"]["D"] = {"type": "values", "hiddenValues": ["West"]}
    find_replace(sheet, "Wireless Mouse", "Wireless Mouse Pro")
    sheet["cells"]["B1"].setdefault("format", {})["fontColor"] = "#0000ff"
    state["namedRanges"]["SalesRegion"] = "Sales!D2:D41"


def solve_task_h39(state):
    """Merge + Performance Summary + MIN/MAX/SUM formulas + CF on totals."""
    sheet = state["sheets"][0]
    sheet["mergedCells"].append("A44:D44")
    sheet["cells"]["A44"] = {
        "value": "Performance Summary", "formula": None,
        "format": {"bold": True, "horizontalAlign": "center"}
    }
    mn_qty = min_col(sheet, "E", 2, 41)
    mx_price = max_col(sheet, "F", 2, 41)
    total_rev = sum_col(sheet, "G", 2, 41)
    sheet["cells"]["E44"] = {"value": mn_qty, "formula": "=MIN(E2:E41)", "format": {}}
    sheet["cells"]["F44"] = {"value": mx_price, "formula": "=MAX(F2:F41)", "format": {"numberFormat": "currency"}}
    sheet["cells"]["G44"] = {"value": total_rev, "formula": "=SUM(G2:G41)", "format": {"numberFormat": "currency"}}
    sheet["conditionalFormats"].append({
        "range": "G2:G41",
        "type": "greater_than",
        "value": "10000",
        "value2": "",
        "backgroundColor": "#c6efce"
    })


def solve_task_h40(state):
    """Executive Summary with title merge + 4 formula rows."""
    sales = state["sheets"][0]
    emp = state["sheets"][1]
    inv = state["sheets"][2]
    total_rev = sum_col(sales, "G", 2, 41)
    total_payroll = sum_col(emp, "D", 2, 26)
    avg_salary = avg_col(emp, "D", 2, 26)
    inv_items = counta_col(inv, "B", 2, 31)

    es = create_empty_sheet("Executive Summary")
    es["cells"]["A1"] = {"value": "Company Dashboard", "formula": None, "format": {"bold": True}}
    es["mergedCells"].append("A1:B1")
    es["cells"]["A3"] = {"value": "Total Revenue", "formula": None, "format": {"bold": True}}
    es["cells"]["B3"] = {"value": total_rev, "formula": "=SUM(Sales!G2:G41)", "format": {"numberFormat": "currency"}}
    es["cells"]["A4"] = {"value": "Total Payroll", "formula": None, "format": {"bold": True}}
    es["cells"]["B4"] = {"value": total_payroll, "formula": "=SUM(Employees!D2:D26)", "format": {"numberFormat": "currency"}}
    es["cells"]["A5"] = {"value": "Average Salary", "formula": None, "format": {"bold": True}}
    es["cells"]["B5"] = {"value": avg_salary, "formula": "=AVERAGE(Employees!D2:D26)", "format": {"numberFormat": "currency"}}
    es["cells"]["A6"] = {"value": "Inventory Items", "formula": None, "format": {"bold": True}}
    es["cells"]["B6"] = {"value": inv_items, "formula": "=COUNTA(Inventory!B2:B31)", "format": {}}
    state["sheets"].append(es)
    state["activeSheet"] = len(state["sheets"]) - 1


# -- solver registry ----------------------------------------------------------

SOLVERS = {}
for _prefix in ("e", "m", "h"):
    for _i in range(1, 41):
        _key = f"task_{_prefix}{_i}"
        _fn = f"solve_task_{_prefix}{_i}"
        if _fn in globals():
            SOLVERS[_key] = globals()[_fn]


# -- server management -------------------------------------------------------

def generate_seed_state():
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
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def find_free_port(start=9600):
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
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# -- task runner --------------------------------------------------------------

def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url, seed_state):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        resp = requests.put(
            f"{server_url}/api/state",
            json=deepcopy(seed_state),
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state: HTTP {resp.status_code}"
        state = resp.json()

        solver(state)

        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
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
    parser = argparse.ArgumentParser(description="Google Sheets real-task sanity check")
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9600, help="Base port for servers")
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
