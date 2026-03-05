#!/usr/bin/env python3
"""
Sanity check for Clio Matters function-test tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_function.py                     # All tasks, sequential
    python3 sanity_check_function.py --workers N          # N parallel environments
    python3 sanity_check_function.py --task-id task_5     # Single task
    python3 sanity_check_function.py --port 9000          # Custom base port
"""
import argparse
import importlib.util
import json
import os
import signal
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

// Helper: extract numeric suffix from string IDs like 'matter_120'
function _maxIdNum(items) {
    return Math.max(...items.map(item => {
        const parts = String(item.id).split('_');
        return parseInt(parts[parts.length - 1], 10);
    }).filter(n => !isNaN(n)));
}

const state = {
    _seedVersion: SEED_DATA_VERSION,
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    users: JSON.parse(JSON.stringify(USERS)),
    groups: JSON.parse(JSON.stringify(GROUPS)),
    contacts: JSON.parse(JSON.stringify(CONTACTS)),
    practiceAreas: JSON.parse(JSON.stringify(PRACTICE_AREAS)),
    customFieldDefinitions: JSON.parse(JSON.stringify(CUSTOM_FIELD_DEFINITIONS)),
    matterTemplates: JSON.parse(JSON.stringify(MATTER_TEMPLATES)),
    numberingScheme: JSON.parse(JSON.stringify(NUMBERING_SCHEME)),
    matters: JSON.parse(JSON.stringify(MATTERS)),
    damages: JSON.parse(JSON.stringify(DAMAGES)),
    medicalProviders: JSON.parse(JSON.stringify(MEDICAL_PROVIDERS)),
    medicalRecords: JSON.parse(JSON.stringify(MEDICAL_RECORDS)),
    medicalBills: JSON.parse(JSON.stringify(MEDICAL_BILLS)),
    settlements: JSON.parse(JSON.stringify(SETTLEMENTS)),
    timeEntries: JSON.parse(JSON.stringify(TIME_ENTRIES)),
    expenses: JSON.parse(JSON.stringify(EXPENSES)),
    activityLog: JSON.parse(JSON.stringify(ACTIVITY_LOG)),
    notificationSettings: JSON.parse(JSON.stringify(NOTIFICATION_SETTINGS)),
    firmSettings: JSON.parse(JSON.stringify(FIRM_SETTINGS)),
    deletedMatters: JSON.parse(JSON.stringify(DELETED_MATTERS)),
    expenseCategories: JSON.parse(JSON.stringify(EXPENSE_CATEGORIES)),
    currencies: JSON.parse(JSON.stringify(CURRENCIES)),
    relationshipTypes: JSON.parse(JSON.stringify(RELATIONSHIP_TYPES)),
    _nextMatterId: MATTERS.length > 0 ? _maxIdNum(MATTERS) + 1 : 121,
    _nextContactId: CONTACTS.length > 0 ? _maxIdNum(CONTACTS) + 1 : 61,
    _nextDamageId: DAMAGES.length > 0 ? _maxIdNum(DAMAGES) + 1 : 31,
    _nextMedicalProviderId: MEDICAL_PROVIDERS.length > 0 ? _maxIdNum(MEDICAL_PROVIDERS) + 1 : 9,
    _nextMedicalRecordId: MEDICAL_RECORDS.length > 0 ? _maxIdNum(MEDICAL_RECORDS) + 1 : 16,
    _nextMedicalBillId: MEDICAL_BILLS.length > 0 ? _maxIdNum(MEDICAL_BILLS) + 1 : 16,
    _nextTimeEntryId: TIME_ENTRIES.length > 0 ? _maxIdNum(TIME_ENTRIES) + 1 : 201,
    _nextExpenseId: EXPENSES.length > 0 ? _maxIdNum(EXPENSES) + 1 : 81,
    _nextLogId: ACTIVITY_LOG.length > 0 ? _maxIdNum(ACTIVITY_LOG) + 1 : 151,
    _nextFolderId: 500,
};
process.stdout.write(JSON.stringify(state));
"""


# ── helpers ──────────────────────────────────────────────────────────

def find_matter_by_number(state, number):
    """Find a matter by its number field."""
    for m in state["matters"]:
        if m["number"] == number:
            return m
    raise ValueError(f"Matter not found: number={number!r}")


def find_damage(state, matter_id, name_contains):
    """Find a damage by matter ID and name substring (case-insensitive)."""
    for d in state["damages"]:
        if d["matterId"] == matter_id and name_contains.lower() in d["name"].lower():
            return d
    raise ValueError(f"Damage not found: matterId={matter_id!r}, name contains {name_contains!r}")


def find_provider(state, matter_id, contact_id):
    """Find a medical provider by matter ID and contact ID."""
    for mp in state["medicalProviders"]:
        if mp["matterId"] == matter_id and mp["contactId"] == contact_id:
            return mp
    raise ValueError(f"Provider not found: matterId={matter_id!r}, contactId={contact_id!r}")


def find_practice_area(state, name):
    """Find a practice area by name."""
    for pa in state["practiceAreas"]:
        if pa["name"] == name:
            return pa
    raise ValueError(f"Practice area not found: {name!r}")


def find_template(state, name):
    """Find a template by name."""
    for t in state["matterTemplates"]:
        if t["name"] == name:
            return t
    raise ValueError(f"Template not found: {name!r}")


def ensure_settlement(state, matter_id):
    """Ensure a settlement entry exists for the given matter."""
    if matter_id not in state["settlements"]:
        state["settlements"][matter_id] = {
            "recoveries": [],
            "legalFees": [],
            "nonMedicalLiens": [],
            "outstandingBalances": [],
        }
    return state["settlements"][matter_id]


# ── solve functions ──────────────────────────────────────────────────

def solve_task_1(state):
    """Change matter 00001-Patterson status to pending."""
    matter = find_matter_by_number(state, "00001")
    matter["status"] = "pending"
    matter["pendingDate"] = "2026-03-02"


def solve_task_2(state):
    """Close matter 00002-Johnson."""
    matter = find_matter_by_number(state, "00002")
    matter["status"] = "closed"
    matter["closedDate"] = "2026-03-02"


def solve_task_3(state):
    """Reopen matter 00003-Russo."""
    matter = find_matter_by_number(state, "00003")
    matter["status"] = "open"


def solve_task_4(state):
    """Create new matter Garcia v. Bay Area Taxi."""
    next_id = state.get("_nextMatterId", 121)
    number = str(next_id).zfill(5)
    matter = {
        "id": f"matter_{next_id}",
        "number": number,
        "displayNumber": f"{number}-Patterson",
        "description": "Garcia v. Bay Area Taxi - Rear-end collision at stoplight",
        "status": "open",
        "billingMethod": "contingency",
        "clientId": "contact_1",
        "responsibleAttorneyId": "user_2",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_1",
        "stageId": None,
        "openDate": "2026-03-02",
        "pendingDate": None,
        "closedDate": None,
        "createdDate": "2026-03-02T00:00:00Z",
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True,
            "method": "contingency",
            "currency": "USD",
            "rates": [],
            "budget": 0,
            "budgetUsed": 0,
            "trustBalance": 0,
            "minimumTrust": 0,
            "contingencyFee": None,
            "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False,
        "deletedAt": None,
    }
    state["matters"].append(matter)
    state["_nextMatterId"] = next_id + 1


def solve_task_5(state):
    """Change matter 00004 responsible attorney to user_2."""
    matter = find_matter_by_number(state, "00004")
    matter["responsibleAttorneyId"] = "user_2"


def solve_task_6(state):
    """Change matter 00005 practice area to Employment Law (pa_6)."""
    matter = find_matter_by_number(state, "00005")
    matter["practiceAreaId"] = "pa_6"


def solve_task_7(state):
    """Change matter 00006 billing method to hourly."""
    matter = find_matter_by_number(state, "00006")
    matter["billingMethod"] = "hourly"
    matter["billing"]["method"] = "hourly"


def solve_task_8(state):
    """Delete matter 00008-Mills."""
    idx = None
    for i, m in enumerate(state["matters"]):
        if m["number"] == "00008":
            idx = i
            break
    if idx is not None:
        matter = state["matters"].pop(idx)
        matter["deletedDate"] = "2026-03-02T00:00:00Z"
        state["deletedMatters"].append(matter)


def solve_task_9(state):
    """Recover deleted matter 00099-TestMatter."""
    idx = None
    for i, m in enumerate(state["deletedMatters"]):
        if m.get("number") == "00099" or "Test Matter" in m.get("description", ""):
            idx = i
            break
    if idx is not None:
        matter = state["deletedMatters"].pop(idx)
        matter["status"] = "open"
        state["matters"].append(matter)


def solve_task_10(state):
    """Duplicate matter 00001-Patterson."""
    source = find_matter_by_number(state, "00001")
    next_id = state.get("_nextMatterId", 121)
    number = str(next_id).zfill(5)
    copy = deepcopy(source)
    copy["id"] = f"matter_{next_id}"
    copy["number"] = number
    copy["displayNumber"] = f"{number}-Patterson"
    copy["description"] = source["description"] + " (Copy)"
    copy["status"] = "open"
    copy["createdDate"] = "2026-03-02T00:00:00Z"
    state["matters"].append(copy)
    state["_nextMatterId"] = next_id + 1


def solve_task_11(state):
    """Update matter 00007 description."""
    matter = find_matter_by_number(state, "00007")
    matter["description"] = "Okafor v. HomeComfort Appliances - Defective space heater causing severe burns and smoke inhalation"


def solve_task_12(state):
    """Set matter 00010 client reference number."""
    matter = find_matter_by_number(state, "00010")
    matter["clientReferenceNumber"] = "PI-2024-0601-REV"


def solve_task_13(state):
    """Set matter 00005 location."""
    matter = find_matter_by_number(state, "00005")
    matter["location"] = "San Francisco County Superior Court"


def solve_task_14(state):
    """Change matter 00010 open date."""
    matter = find_matter_by_number(state, "00010")
    matter["openDate"] = "2024-12-01"


def solve_task_15(state):
    """Set matter 00002 permissions to specific with Diana Reyes (user_3)."""
    matter = find_matter_by_number(state, "00002")
    matter["permissions"]["type"] = "specific"
    if "user_3" not in matter["permissions"].get("userIds", []):
        matter["permissions"].setdefault("userIds", []).append("user_3")


def solve_task_16(state):
    """Add Priya Sharma (user_5) to blocked users on matter 00001."""
    matter = find_matter_by_number(state, "00001")
    if "user_5" not in matter.get("blockedUsers", []):
        matter.setdefault("blockedUsers", []).append("user_5")


def solve_task_17(state):
    """Add/change relationship with contact_45 to 'Parent' on matter 00001."""
    matter = find_matter_by_number(state, "00001")
    # Check if contact_45 already exists in relationships
    found = False
    for rel in matter.get("relationships", []):
        if rel.get("contactId") == "contact_45":
            rel["relationship"] = "Parent"
            found = True
            break
    if not found:
        matter.setdefault("relationships", []).append({
            "contactId": "contact_45",
            "relationship": "Parent",
            "billRecipient": False,
        })


def solve_task_18(state):
    """Set matter 00005 custom field cf_1 (Court Case Number)."""
    matter = find_matter_by_number(state, "00005")
    matter["customFields"]["cf_1"] = "SM-2024-CV-19876"


def solve_task_19(state):
    """Change matter 00001 budget to 75000."""
    matter = find_matter_by_number(state, "00001")
    matter["billing"]["budget"] = 75000


def solve_task_20(state):
    """Set matter 00004 minimum trust to 5000."""
    matter = find_matter_by_number(state, "00004")
    matter["billing"]["minimumTrust"] = 5000


def solve_task_21(state):
    """Change matter 00007 contingency fee to 33.33%."""
    matter = find_matter_by_number(state, "00007")
    matter["billing"]["contingencyFee"]["percentage"] = 33.33


def solve_task_22(state):
    """Change matter 00004 deduction order to fees_first."""
    matter = find_matter_by_number(state, "00004")
    matter["personalInjury"]["deductionOrder"] = "fees_first"


def solve_task_23(state):
    """Add damage 'Lost Wages - Q1 2025' to matter_1."""
    next_id = state.get("_nextDamageId", 31)
    state["damages"].append({
        "id": f"dmg_{next_id}",
        "matterId": "matter_1",
        "name": "Lost Wages - Q1 2025",
        "amount": 12500,
        "type": "special",
    })
    state["_nextDamageId"] = next_id + 1


def solve_task_24(state):
    """Delete emergency room visit damage from matter_1."""
    state["damages"] = [
        d for d in state["damages"]
        if not (d["matterId"] == "matter_1" and "emergency room visit" in d["name"].lower())
    ]


def solve_task_25(state):
    """Change 'Pain and suffering' amount to 200000 on matter_1."""
    dmg = find_damage(state, "matter_1", "pain and suffering")
    dmg["amount"] = 200000


def solve_task_26(state):
    """Add medical provider contact_60 (Dr. Michael Reeves Chiropractic) to matter_1."""
    next_id = state.get("_nextMedicalProviderId", 9)
    state["medicalProviders"].append({
        "id": f"mp_{next_id}",
        "matterId": "matter_1",
        "contactId": "contact_60",
        "description": "Chiropractic evaluation for cervical spine",
        "firstTreatmentDate": None,
        "lastTreatmentDate": None,
        "treatmentComplete": False,
        "recordRequestDate": None,
        "recordFollowUpDate": None,
        "recordStatus": "not_requested",
        "billRequestDate": None,
        "billFollowUpDate": None,
        "billStatus": "not_requested",
    })
    state["_nextMedicalProviderId"] = next_id + 1


def solve_task_27(state):
    """Delete medical provider with contact_56 from matter_1."""
    state["medicalProviders"] = [
        mp for mp in state["medicalProviders"]
        if not (mp["matterId"] == "matter_1" and mp["contactId"] == "contact_56")
    ]
    # Also remove associated records and bills
    state["medicalRecords"] = [
        mr for mr in state["medicalRecords"]
        if not (mr["matterId"] == "matter_1" and mr["providerId"] == "mp_2")
    ]
    state["medicalBills"] = [
        mb for mb in state["medicalBills"]
        if not (mb["matterId"] == "matter_1" and mb["providerId"] == "mp_2")
    ]


def solve_task_28(state):
    """Add recovery from State Farm (contact_58) for $150k to matter_1 settlement."""
    settlement = ensure_settlement(state, "matter_1")
    settlement["recoveries"].append({
        "id": "rec_new_1",
        "sourceContactId": "contact_58",
        "sourceName": "State Farm Insurance - Liens",
        "amount": 150000,
    })


def solve_task_29(state):
    """Change legal fee rate on matter_3 settlement from 33.33 to 40."""
    settlement = state["settlements"]["matter_3"]
    for lf in settlement["legalFees"]:
        if lf.get("id") == "lf_1" or lf.get("recoveryId") == "rec_1":
            lf["rate"] = 40
            break


def solve_task_30(state):
    """Add non-medical lien from CalComp (contact_42) to matter_1 settlement."""
    settlement = ensure_settlement(state, "matter_1")
    settlement["nonMedicalLiens"].append({
        "id": "nml_new_1",
        "holderContactId": "contact_42",
        "description": "Workers compensation lien",
        "amount": 15000,
        "reduction": 3000,
    })


def solve_task_31(state):
    """Add outstanding balance to matter_1 settlement."""
    settlement = ensure_settlement(state, "matter_1")
    settlement["outstandingBalances"].append({
        "id": "ob_new_1",
        "responsibility": "client",
        "holderContactId": "contact_66",
        "description": "Unpaid radiology balance",
        "balanceOwing": 2500,
        "reduction": 500,
    })


def solve_task_32(state):
    """Create practice area 'Civil Rights'."""
    state["practiceAreas"].append({
        "id": "pa_14",
        "name": "Civil Rights",
        "stages": [],
    })


def solve_task_33(state):
    """Delete practice area 'Environmental Law'."""
    state["practiceAreas"] = [
        pa for pa in state["practiceAreas"] if pa["name"] != "Environmental Law"
    ]


def solve_task_34(state):
    """Rename 'Corporate/Business' to 'Corporate & Transactional'."""
    pa = find_practice_area(state, "Corporate/Business")
    pa["name"] = "Corporate & Transactional"


def solve_task_35(state):
    """Add 'Appeals' stage to Criminal Defense."""
    pa = find_practice_area(state, "Criminal Defense")
    max_order = max((s["order"] for s in pa["stages"]), default=-1)
    pa["stages"].append({
        "id": f"stage_3_{len(pa['stages']) + 1}",
        "name": "Appeals",
        "order": max_order + 1,
    })


def solve_task_36(state):
    """Delete 'Closing' stage from Real Estate."""
    pa = find_practice_area(state, "Real Estate")
    pa["stages"] = [s for s in pa["stages"] if s["name"] != "Closing"]


def solve_task_37(state):
    """Rename 'Intake' to 'Case Intake' in Personal Injury."""
    pa = find_practice_area(state, "Personal Injury")
    for s in pa["stages"]:
        if s["name"] == "Intake":
            s["name"] = "Case Intake"
            break


def solve_task_38(state):
    """Create template 'Immigration - Work Visa'."""
    state["matterTemplates"].append({
        "id": "template_8",
        "name": "Immigration - Work Visa",
        "isDefault": False,
        "description": "",
        "practiceAreaId": "pa_8",
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
    })


def solve_task_39(state):
    """Delete template 'Estate Planning - Comprehensive'."""
    state["matterTemplates"] = [
        t for t in state["matterTemplates"]
        if t["name"] != "Estate Planning - Comprehensive"
    ]


def solve_task_40(state):
    """Set 'Criminal Defense - Misdemeanor' as default template."""
    for t in state["matterTemplates"]:
        if t["name"] == "Criminal Defense - Misdemeanor":
            t["isDefault"] = True
        elif t["isDefault"]:
            t["isDefault"] = False


def solve_task_41(state):
    """Change numbering separator to '/'."""
    state["numberingScheme"]["separator"] = "/"


def solve_task_42(state):
    """Change number padding to 6."""
    state["numberingScheme"]["numberPadding"] = 6


def solve_task_43(state):
    """Disable budget_threshold notification."""
    state["notificationSettings"]["budget_threshold"] = False


def solve_task_44(state):
    """Disable matter_updates, keep trust_balance enabled."""
    state["notificationSettings"]["matter_updates"] = False
    state["notificationSettings"]["trust_balance"] = True


def solve_task_45(state):
    """Move matter 00010 to Investigation stage (stage_1_2)."""
    matter = find_matter_by_number(state, "00010")
    matter["stageId"] = "stage_1_2"


def solve_task_46(state):
    """Set matter 00001 currency to EUR."""
    matter = find_matter_by_number(state, "00001")
    matter["billing"]["currency"] = "EUR"


def solve_task_47(state):
    """Change matter 00005 originating attorney to user_1."""
    matter = find_matter_by_number(state, "00005")
    matter["originatingAttorneyId"] = "user_1"


def solve_task_48(state):
    """Change matter 00010 client to contact_61 (Nancy Whitfield)."""
    matter = find_matter_by_number(state, "00010")
    matter["clientId"] = "contact_61"


def solve_task_49(state):
    """Change matter 00009 status from pending to open."""
    matter = find_matter_by_number(state, "00009")
    matter["status"] = "open"


def solve_task_50(state):
    """Set matter 00001 custom field cf_7 (Judge Assigned)."""
    matter = find_matter_by_number(state, "00001")
    matter["customFields"]["cf_7"] = "Hon. Patricia Williams"


def solve_task_51(state):
    """Create contact Michael Rivera."""
    next_id = state.get("_nextContactId", 61)
    state["contacts"].append({
        "id": f"contact_{next_id}",
        "type": "person",
        "firstName": "Michael",
        "lastName": "Rivera",
        "companyName": None,
        "displayName": "Michael Rivera",
        "email": "mrivera@email.com",
        "phone": "(555) 999-1234",
        "address": "",
        "tags": [],
        "createdAt": "2026-03-02T00:00:00Z",
    })
    state["_nextContactId"] = next_id + 1


def solve_task_52(state):
    """Change 'Lumbar MRI and diagnostic imaging' type to general on matter_1."""
    dmg = find_damage(state, "matter_1", "Lumbar MRI")
    dmg["type"] = "general"


def solve_task_53(state):
    """Delete recovery from ABC Insurance Co. on matter_3 settlement."""
    settlement = state["settlements"]["matter_3"]
    settlement["recoveries"] = [
        r for r in settlement["recoveries"]
        if "ABC Insurance" not in r.get("sourceName", "") and r.get("id") != "rec_1"
    ]


def solve_task_54(state):
    """Change recovery amount on matter_21 to 55000."""
    settlement = state["settlements"]["matter_21"]
    for r in settlement["recoveries"]:
        if r.get("id") == "rec_3" or "SFMTA" in r.get("sourceName", ""):
            r["amount"] = 55000
            break


def solve_task_55(state):
    """Change matter 00001 responsible staff to user_9."""
    matter = find_matter_by_number(state, "00001")
    matter["responsibleStaffId"] = "user_9"


SOLVERS = {
    "task_1": solve_task_1,
    "task_2": solve_task_2,
    "task_3": solve_task_3,
    "task_4": solve_task_4,
    "task_5": solve_task_5,
    "task_6": solve_task_6,
    "task_7": solve_task_7,
    "task_8": solve_task_8,
    "task_9": solve_task_9,
    "task_10": solve_task_10,
    "task_11": solve_task_11,
    "task_12": solve_task_12,
    "task_13": solve_task_13,
    "task_14": solve_task_14,
    "task_15": solve_task_15,
    "task_16": solve_task_16,
    "task_17": solve_task_17,
    "task_18": solve_task_18,
    "task_19": solve_task_19,
    "task_20": solve_task_20,
    "task_21": solve_task_21,
    "task_22": solve_task_22,
    "task_23": solve_task_23,
    "task_24": solve_task_24,
    "task_25": solve_task_25,
    "task_26": solve_task_26,
    "task_27": solve_task_27,
    "task_28": solve_task_28,
    "task_29": solve_task_29,
    "task_30": solve_task_30,
    "task_31": solve_task_31,
    "task_32": solve_task_32,
    "task_33": solve_task_33,
    "task_34": solve_task_34,
    "task_35": solve_task_35,
    "task_36": solve_task_36,
    "task_37": solve_task_37,
    "task_38": solve_task_38,
    "task_39": solve_task_39,
    "task_40": solve_task_40,
    "task_41": solve_task_41,
    "task_42": solve_task_42,
    "task_43": solve_task_43,
    "task_44": solve_task_44,
    "task_45": solve_task_45,
    "task_46": solve_task_46,
    "task_47": solve_task_47,
    "task_48": solve_task_48,
    "task_49": solve_task_49,
    "task_50": solve_task_50,
    "task_51": solve_task_51,
    "task_52": solve_task_52,
    "task_53": solve_task_53,
    "task_54": solve_task_54,
    "task_55": solve_task_55,
}


# ── server management ────────────────────────────────────────────────

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
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start+100}")


def start_server(port):
    """Start the Clio Matters server on the given port."""
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait for server to be ready
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


# ── task runner ──────────────────────────────────────────────────────

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


def run_single_task(task, server_url):
    """Reset → solve → verify for a single task."""
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        # Wait briefly for reset to settle
        time.sleep(0.3)

        # 2. Read seed state
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply the solve function
        solver(state)

        # 4. Write solved state back
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run the verifier
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
        # Seed the server with initial state so GET /api/state works
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url)
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
            return run_single_task(task, server_url)
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


# ── main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Clio Matters function-task sanity check")
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
