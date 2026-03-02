#!/usr/bin/env python3
"""
Sanity check for Clio Matters real-task verifiers.

For each task, directly constructs the expected end-state (bypassing the agent),
then runs the verifier and asserts it returns True. This confirms that verifiers
correctly recognize a solved task.

Usage:
    python3 sanity_check_real.py                      # All tasks, sequential
    python3 sanity_check_real.py --workers N           # N parallel environments
    python3 sanity_check_real.py --task-id task_e1     # Single task
    python3 sanity_check_real.py --port 9500           # Custom base port
"""
import argparse
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "tasks.json"

NOW = "2026-03-02T12:00:00Z"
TODAY = "2026-03-02"

# ---------------------------------------------------------------------------
# Seed state loader (evaluates data.js via Node)
# ---------------------------------------------------------------------------
_SEED_STATE_JS = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

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


def generate_seed_state():
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to generate seed state:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------
def find_matter_by_desc(state, *keywords):
    """Find a matter whose description contains all keywords (case-insensitive)."""
    for m in state["matters"]:
        desc = (m.get("description") or "").lower()
        if all(kw.lower() in desc for kw in keywords):
            return m
    raise ValueError(f"Matter not found with keywords: {keywords}")


def find_matter_by_number(state, number):
    for m in state["matters"]:
        if m["number"] == number:
            return m
    raise ValueError(f"Matter not found: number={number!r}")


def find_matter_by_id(state, matter_id):
    for m in state["matters"]:
        if m["id"] == matter_id:
            return m
    raise ValueError(f"Matter not found: id={matter_id!r}")


def find_practice_area(state, name):
    for pa in state["practiceAreas"]:
        if pa["name"] == name:
            return pa
    raise ValueError(f"Practice area not found: {name!r}")


def find_template(state, name):
    for t in state["matterTemplates"]:
        if t["name"] == name:
            return t
    raise ValueError(f"Template not found: {name!r}")


def find_contact_by_name(state, name):
    for c in state["contacts"]:
        if name.lower() in (c.get("displayName") or "").lower():
            return c
    raise ValueError(f"Contact not found: {name!r}")


def find_user_by_name(state, name):
    for u in state["users"]:
        if name.lower() in u["name"].lower():
            return u
    raise ValueError(f"User not found: {name!r}")


def ensure_settlement(state, matter_id):
    if matter_id not in state["settlements"]:
        state["settlements"][matter_id] = {
            "recoveries": [],
            "legalFees": [],
            "nonMedicalLiens": [],
            "outstandingBalances": [],
        }
    return state["settlements"][matter_id]


def next_matter_id(state):
    mid = state.get("_nextMatterId", 121)
    state["_nextMatterId"] = mid + 1
    return mid


def next_damage_id(state):
    did = state.get("_nextDamageId", 39)
    state["_nextDamageId"] = did + 1
    return did


def next_provider_id(state):
    pid = state.get("_nextMedicalProviderId", 13)
    state["_nextMedicalProviderId"] = pid + 1
    return pid


# ---------------------------------------------------------------------------
# Solve functions — one per task
# ---------------------------------------------------------------------------

# ---- Easy ----

def solve_task_e1(state):
    """Close the Patterson bus accident case."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    m["status"] = "closed"
    m["closedDate"] = TODAY


def solve_task_e2(state):
    """Reopen the Russo v. Lyft rideshare accident matter."""
    m = find_matter_by_desc(state, "Russo", "Lyft")
    m["status"] = "open"
    m["closedDate"] = None


def solve_task_e3(state):
    """Mark the Johnson v. Whole Foods case as pending."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    m["status"] = "pending"
    m["pendingDate"] = TODAY


def solve_task_e4(state):
    """Turn off budget threshold notifications."""
    state["notificationSettings"]["budget_threshold"] = False


def solve_task_e5(state):
    """Change the matter numbering separator to a period."""
    state["numberingScheme"]["separator"] = "."


def solve_task_e6(state):
    """Set Criminal Defense - Misdemeanor template as default."""
    for t in state["matterTemplates"]:
        t["isDefault"] = (t["name"] == "Criminal Defense - Misdemeanor")


def solve_task_e7(state):
    """Delete the Estate Planning - Comprehensive template."""
    state["matterTemplates"] = [
        t for t in state["matterTemplates"]
        if t["name"] != "Estate Planning - Comprehensive"
    ]


def solve_task_e8(state):
    """Rename Corporate/Business to Business Law."""
    pa = find_practice_area(state, "Corporate/Business")
    pa["name"] = "Business Law"


def solve_task_e9(state):
    """Move Dimitriou dog bite matter to Investigation stage."""
    m = find_matter_by_desc(state, "Dimitriou", "dog bite")
    m["stageId"] = "stage_1_2"


def solve_task_e10(state):
    """Disable matter deletion notifications."""
    state["notificationSettings"]["matter_deletions"] = False


def solve_task_e11(state):
    """Change number padding to 6."""
    state["numberingScheme"]["numberPadding"] = 6


def solve_task_e12(state):
    """Delete the Closing stage from Real Estate."""
    pa = find_practice_area(state, "Real Estate")
    pa["stages"] = [s for s in pa["stages"] if s["name"] != "Closing"]
    for i, s in enumerate(pa["stages"]):
        s["order"] = i


def solve_task_e13(state):
    """Delete the Mills motorcycle collision matter."""
    m = find_matter_by_desc(state, "Mills", "Motorcycle")
    idx = next(i for i, x in enumerate(state["matters"]) if x["id"] == m["id"])
    matter = state["matters"].pop(idx)
    matter["deletedDate"] = NOW
    state["deletedMatters"].append(matter)


def solve_task_e14(state):
    """Recover the Smith consultation from recovery bin."""
    idx = None
    for i, dm in enumerate(state["deletedMatters"]):
        if "Smith Consultation" in dm.get("description", ""):
            idx = i
            break
    if idx is not None:
        matter = state["deletedMatters"].pop(idx)
        matter["status"] = "open"
        state["matters"].append(matter)


def solve_task_e15(state):
    """Add Appeals stage to Criminal Defense."""
    pa = find_practice_area(state, "Criminal Defense")
    pa["stages"].append({
        "id": f"stage_3_{len(pa['stages']) + 1}",
        "name": "Appeals",
        "order": len(pa["stages"]),
    })


def solve_task_e16(state):
    """Change firm default template to PI - Slip and Fall."""
    state["firmSettings"]["defaultTemplateId"] = "template_7"


def solve_task_e17(state):
    """Switch deduction order on Washington case to fees first."""
    m = find_matter_by_desc(state, "Washington", "Pacific Steel")
    if m.get("personalInjury") is None:
        m["personalInjury"] = {}
    m["personalInjury"]["deductionOrder"] = "fees_first"


def solve_task_e18(state):
    """Change Patterson case currency to British Pounds."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    m["billing"]["currency"] = "GBP"


def solve_task_e19(state):
    """Reassign DeLuca felony DUI to Robert Jackson."""
    m = find_matter_by_desc(state, "DeLuca", "Felony DUI")
    m["responsibleAttorneyId"] = "user_8"


def solve_task_e20(state):
    """Rename Intake stage under Personal Injury to Case Intake."""
    pa = find_practice_area(state, "Personal Injury")
    for s in pa["stages"]:
        if s["id"] == "stage_1_1":
            s["name"] = "Case Intake"


# ---- Medium ----

def solve_task_m1(state):
    """Create Civil Rights practice area with 3 stages."""
    max_num = max(
        int(pa["id"].split("_")[1])
        for pa in state["practiceAreas"]
    )
    pa_id = f"pa_{max_num + 1}"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Civil Rights",
        "stages": [
            {"id": f"stage_{max_num + 1}_1", "name": "Investigation", "order": 0},
            {"id": f"stage_{max_num + 1}_2", "name": "Filing", "order": 1},
            {"id": f"stage_{max_num + 1}_3", "name": "Resolution", "order": 2},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })


def solve_task_m2(state):
    """Add $50,000 general damage to Johnson v. Whole Foods."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": m["id"],
        "name": "Pain and suffering",
        "amount": 50000,
        "type": "general",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })


def solve_task_m3(state):
    """Change McCarthy responsible attorney to Marcus Williams and move to Litigation."""
    m = find_matter_by_desc(state, "McCarthy", "pedestrian")
    m["responsibleAttorneyId"] = "user_2"
    m["stageId"] = "stage_1_4"


def solve_task_m4(state):
    """Create Immigration - Work Visa template."""
    max_num = max(
        int(t["id"].split("_")[1])
        for t in state["matterTemplates"]
    )
    state["matterTemplates"].append({
        "id": f"template_{max_num + 1}",
        "name": "Immigration - Work Visa",
        "isDefault": False,
        "description": "Template for immigration work visa matters",
        "practiceAreaId": "pa_8",
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })


def solve_task_m5(state):
    """Add $250,000 recovery to Patterson settlement."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    settlement = ensure_settlement(state, m["id"])
    next_id = len(settlement["recoveries"]) + 1
    settlement["recoveries"].append({
        "id": f"rec_{next_id}",
        "amount": 250000,
        "sourceContactId": "contact_58",
        "sourceName": "State Farm Insurance - Liens",
    })


def solve_task_m6(state):
    """Restrict Johnson v. Whole Foods permissions to Litigation Team."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    m["permissions"] = {
        "type": "specific",
        "userIds": [],
        "groupIds": ["group_1"],
    }


def solve_task_m7(state):
    """Update numbering to slash separator and 6-digit padding."""
    state["numberingScheme"]["separator"] = "/"
    state["numberingScheme"]["numberPadding"] = 6


def solve_task_m8(state):
    """Add $15,000 non-medical lien from CalComp to Patterson settlement."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    settlement = ensure_settlement(state, m["id"])
    next_id = len(settlement["nonMedicalLiens"]) + 1
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{next_id}",
        "holderContactId": "contact_42",
        "description": "CalComp Workers Compensation lien",
        "amount": 15000,
        "reduction": 0,
    })


def solve_task_m9(state):
    """Add Dr. Michael Reeves Chiropractic as medical provider on Johnson case."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    pid = next_provider_id(state)
    state["medicalProviders"].append({
        "id": f"mp_{pid}",
        "matterId": m["id"],
        "contactId": "contact_60",
        "description": "Post-surgical pain management",
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


def solve_task_m10(state):
    """Close Baptiste contested divorce and set stage to Trial/Resolution."""
    m = find_matter_by_desc(state, "Baptiste", "Contested divorce")
    m["status"] = "closed"
    m["closedDate"] = TODAY
    m["stageId"] = "stage_2_5"


def solve_task_m11(state):
    """Remove all damages from Russo v. Lyft."""
    m = find_matter_by_desc(state, "Russo", "Lyft")
    state["damages"] = [d for d in state["damages"] if d["matterId"] != m["id"]]


def solve_task_m12(state):
    """Set custom fields on Doyle scaffolding case."""
    m = find_matter_by_desc(state, "Doyle", "scaffolding")
    m["customFields"]["cf_1"] = "SM-2025-PI-4421"
    m["customFields"]["cf_7"] = "Hon. Patricia Chen"


def solve_task_m13(state):
    """Create new Real Estate matter for Robert O'Malley."""
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-OMalley",
        "description": "O'Malley Rental Property Dispute",
        "status": "open",
        "billingMethod": "flat_rate",
        "clientId": "contact_6",
        "responsibleAttorneyId": "user_13",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_4",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "flat_rate", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_m14(state):
    """Add 33.33% contingency legal fee to Okafor burn case settlement."""
    m = find_matter_by_desc(state, "Okafor", "burn")
    settlement = ensure_settlement(state, m["id"])
    next_id = len(settlement["legalFees"]) + 1
    settlement["legalFees"].append({
        "id": f"lf_{next_id}",
        "recoveryId": None,
        "recipientId": "user_2",
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })


def solve_task_m15(state):
    """Block Priya Sharma from Blackwell divorce and restrict to Family Law Division."""
    m = find_matter_by_desc(state, "Blackwell", "Divorce", "High-asset")
    if "user_5" not in m.get("blockedUsers", []):
        m.setdefault("blockedUsers", []).append("user_5")
    m["permissions"] = {
        "type": "specific",
        "userIds": [],
        "groupIds": ["group_2"],
    }


def solve_task_m16(state):
    """Add State Farm Insurance as Insurance Adjuster on Doyle case."""
    m = find_matter_by_desc(state, "Doyle", "scaffolding")
    m.setdefault("relationships", []).append({
        "contactId": "contact_58",
        "relationship": "Insurance Adjuster",
        "billRecipient": False,
    })


def solve_task_m17(state):
    """Change Vertex Series B currency to GBP and budget to 100000."""
    m = find_matter_by_desc(state, "Vertex", "Series B")
    m["billing"]["currency"] = "GBP"
    m["billing"]["budget"] = 100000


def solve_task_m18(state):
    """Add $200,000 special damage to Sullivan-Wright case."""
    m = find_matter_by_desc(state, "Sullivan-Wright")
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": m["id"],
        "name": "Lost future earnings",
        "amount": 200000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })


def solve_task_m19(state):
    """Delete Plea Negotiation from Criminal Defense, rename Pre-Trial."""
    pa = find_practice_area(state, "Criminal Defense")
    pa["stages"] = [s for s in pa["stages"] if s["name"] != "Plea Negotiation"]
    for s in pa["stages"]:
        if s["name"] == "Pre-Trial":
            s["name"] = "Pre-Trial/Plea"
    for i, s in enumerate(pa["stages"]):
        s["order"] = i
    # Clear stageId for matters that were at the deleted stage
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["stageId"] == "stage_3_3":
            m["stageId"] = None


def solve_task_m20(state):
    """Add $5,000 outstanding balance to Patterson settlement."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    settlement = ensure_settlement(state, m["id"])
    next_id = len(settlement["outstandingBalances"]) + 1
    settlement["outstandingBalances"].append({
        "id": f"ob_{next_id}",
        "responsibility": "client",
        "holderContactId": "contact_57",
        "description": "Pacific Physical Therapy Center balance",
        "balanceOwing": 5000,
        "originalAmount": 5000,
        "reduction": 0,
    })


# ---- Hard ----

def solve_task_h1(state):
    """Close all open PI matters in the Demand stage."""
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["stageId"] == "stage_1_3"
                and m["status"] == "open"):
            m["status"] = "closed"
            m["closedDate"] = TODAY


def solve_task_h2(state):
    """Create new PI matter for Aisha Johnson with 40% contingency and $15,000 damage."""
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    matter_id = f"matter_{mid}"
    state["matters"].append({
        "id": matter_id,
        "number": number,
        "displayNumber": f"{number}-Johnson",
        "description": "Johnson v. Restaurant - Slip and fall at restaurant",
        "status": "open",
        "billingMethod": "contingency",
        "clientId": "contact_5",
        "responsibleAttorneyId": "user_2",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_1",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "contingency", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0,
            "contingencyFee": {"userId": "user_2", "percentage": 40},
            "flatRate": None,
        },
        "personalInjury": {"deductionOrder": "fees_first"},
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": matter_id,
        "name": "Emergency room visit",
        "amount": 15000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })


def solve_task_h3(state):
    """Find PI matter with highest budget, change attorney to Diana Reyes."""
    pi_matters = [m for m in state["matters"] if m["practiceAreaId"] == "pa_1"]
    best = max(pi_matters, key=lambda m: m.get("billing", {}).get("budget", 0))
    best["responsibleAttorneyId"] = "user_3"


def solve_task_h4(state):
    """Set up Johnson v. Whole Foods settlement."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 208650,
        "sourceContactId": None,
        "sourceName": "Hartford Insurance",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": "user_2",
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_59",
        "description": "UCSF Medical Center lien",
        "amount": 14500,
        "reduction": 0,
    })


def solve_task_h5(state):
    """Create Appellate Law PA with 4 stages and template."""
    max_num = max(int(pa["id"].split("_")[1]) for pa in state["practiceAreas"])
    pa_id = f"pa_{max_num + 1}"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Appellate Law",
        "stages": [
            {"id": f"stage_{max_num + 1}_1", "name": "Notice of Appeal", "order": 0},
            {"id": f"stage_{max_num + 1}_2", "name": "Briefing", "order": 1},
            {"id": f"stage_{max_num + 1}_3", "name": "Oral Argument", "order": 2},
            {"id": f"stage_{max_num + 1}_4", "name": "Decision", "order": 3},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })
    max_t = max(int(t["id"].split("_")[1]) for t in state["matterTemplates"])
    state["matterTemplates"].append({
        "id": f"template_{max_t + 1}",
        "name": "Appellate Practice - Standard",
        "isDefault": False,
        "description": "Template for appellate matters",
        "practiceAreaId": pa_id,
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })


def solve_task_h6(state):
    """Transfer all Priya Sharma's matters to Kevin Nakamura."""
    for m in state["matters"]:
        if m["responsibleAttorneyId"] == "user_5":
            m["responsibleAttorneyId"] = "user_6"


def solve_task_h7(state):
    """Move all CD matters at Arraignment to Pre-Trial."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_3" and m["stageId"] == "stage_3_1":
            m["stageId"] = "stage_3_2"


def solve_task_h8(state):
    """Update numbering and create matter for Andrew Kim."""
    state["numberingScheme"]["prefix"] = "MLG"
    state["numberingScheme"]["separator"] = "/"
    state["numberingScheme"]["numberPadding"] = 6
    mid = next_matter_id(state)
    number = str(mid).zfill(6)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"MLG/{number}-Kim",
        "description": "Kim Startup Formation",
        "status": "open",
        "billingMethod": "hourly",
        "clientId": "contact_43",
        "responsibleAttorneyId": "user_1",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_5",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "hourly", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h9(state):
    """Okafor burn case: add damage, legal fee, outstanding balance."""
    m = find_matter_by_desc(state, "Okafor", "burn")
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": m["id"],
        "name": "Future reconstructive surgery",
        "amount": 35000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })
    settlement = ensure_settlement(state, m["id"])
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": "user_2",
        "rate": 40,
        "percentage": 40,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": None,
        "description": "Outstanding balance",
        "balanceOwing": 8000,
        "originalAmount": 8000,
        "reduction": 0,
    })


def solve_task_h10(state):
    """Close pending FL matters, move open FL consultation to Filing."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_2" and m["status"] == "pending":
            m["status"] = "closed"
            m["closedDate"] = TODAY
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_2"
                and m["status"] == "open"
                and m["stageId"] == "stage_2_1"):
            m["stageId"] = "stage_2_2"


def solve_task_h11(state):
    """Set up McCarthy pedestrian settlement."""
    m = find_matter_by_desc(state, "McCarthy", "pedestrian")
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 150000,
        "sourceContactId": None,
        "sourceName": "City of San Francisco",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": "user_8",
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": "contact_56",
        "description": "Bay Area Orthopedic Associates",
        "balanceOwing": 25000,
        "originalAmount": 25000,
        "reduction": 0,
    })


def solve_task_h12(state):
    """Reassign Robert Jackson's open PI matters to Marcus Williams."""
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["status"] == "open"
                and m["responsibleAttorneyId"] == "user_8"):
            m["responsibleAttorneyId"] = "user_2"


def solve_task_h13(state):
    """Create two new matters: FL for Baptiste, CD for Hernandez."""
    mid1 = next_matter_id(state)
    number1 = str(mid1).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid1}",
        "number": number1,
        "displayNumber": f"{number1}-Baptiste",
        "description": "Baptiste Family Law Matter",
        "status": "open",
        "billingMethod": "hourly",
        "clientId": "contact_62",
        "responsibleAttorneyId": "user_3",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_2",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "hourly", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })
    mid2 = next_matter_id(state)
    number2 = str(mid2).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid2}",
        "number": number2,
        "displayNumber": f"{number2}-Hernandez",
        "description": "People v. Hernandez - Criminal Defense",
        "status": "open",
        "billingMethod": "flat_rate",
        "clientId": "contact_29",
        "responsibleAttorneyId": "user_8",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_3",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "flat_rate", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h14(state):
    """DeLuca arraignment case: flat rate $15,000, move to Pre-Trial."""
    m = find_matter_by_desc(state, "DeLuca", "Felony DUI")
    m["billingMethod"] = "flat_rate"
    m["billing"]["method"] = "flat_rate"
    m["billing"]["flatRate"] = {"amount": 15000, "userId": m["responsibleAttorneyId"]}
    m["stageId"] = "stage_3_2"


def solve_task_h15(state):
    """Add UCSF Medical Center and Meridian Radiology as providers on McCarthy case."""
    m = find_matter_by_desc(state, "McCarthy", "pedestrian")
    pid1 = next_provider_id(state)
    state["medicalProviders"].append({
        "id": f"mp_{pid1}",
        "matterId": m["id"],
        "contactId": "contact_59",
        "description": "UCSF Medical Center treatment",
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
    pid2 = next_provider_id(state)
    state["medicalProviders"].append({
        "id": f"mp_{pid2}",
        "matterId": m["id"],
        "contactId": "contact_66",
        "description": "Meridian Radiology Associates imaging",
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


def solve_task_h16(state):
    """Delete PI - Slip and Fall template, create PI - Premises Liability."""
    state["matterTemplates"] = [
        t for t in state["matterTemplates"]
        if t["name"] != "Personal Injury - Slip and Fall"
    ]
    max_num = max(
        int(t["id"].split("_")[1])
        for t in state["matterTemplates"]
    )
    state["matterTemplates"].append({
        "id": f"template_{max_num + 1}",
        "name": "Personal Injury - Premises Liability",
        "isDefault": False,
        "description": "Template for premises liability cases",
        "practiceAreaId": "pa_1",
        "billable": True,
        "billingMethod": "contingency",
        "deductionOrder": "fees_first",
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })


def solve_task_h17(state):
    """Washington case: 35% contingency, $120K recovery, Settlement/Trial stage."""
    m = find_matter_by_desc(state, "Washington", "Pacific Steel")
    m["billing"]["contingencyFee"]["percentage"] = 35
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 120000,
        "sourceContactId": "contact_42",
        "sourceName": "CalComp Workers Compensation",
    })
    m["stageId"] = "stage_1_5"


def solve_task_h18(state):
    """Create Appellate Practice PA with 3 stages, move Hernandez armed robbery."""
    max_num = max(int(pa["id"].split("_")[1]) for pa in state["practiceAreas"])
    pa_id = f"pa_{max_num + 1}"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Appellate Practice",
        "stages": [
            {"id": f"stage_{max_num + 1}_1", "name": "Notice of Appeal", "order": 0},
            {"id": f"stage_{max_num + 1}_2", "name": "Brief Writing", "order": 1},
            {"id": f"stage_{max_num + 1}_3", "name": "Oral Argument", "order": 2},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })
    m = find_matter_by_desc(state, "Hernandez", "armed robbery")
    m["practiceAreaId"] = pa_id


def solve_task_h19(state):
    """Add 3 damages to Brennan hotel slip-and-fall."""
    m = find_matter_by_desc(state, "Brennan", "Oceanview")
    for name, amount, dtype in [
        ("Emergency room visit", 8500, "special"),
        ("Wrist surgery", 12000, "special"),
        ("Pain and suffering", 45000, "general"),
    ]:
        did = next_damage_id(state)
        state["damages"].append({
            "id": f"dmg_{did}",
            "matterId": m["id"],
            "name": name,
            "amount": amount,
            "type": dtype,
            "date": None,
            "notes": "",
            "createdDate": NOW,
            "updatedDate": NOW,
        })


def solve_task_h20(state):
    """Set up Fitzgerald medical malpractice settlement."""
    m = find_matter_by_desc(state, "Fitzgerald", "Misdiagnosis")
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 375000,
        "sourceContactId": None,
        "sourceName": "Settlement",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": "user_8",
        "rate": 40,
        "percentage": 40,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": None,
        "description": "Health insurance subrogation lien",
        "amount": 20000,
        "reduction": 0,
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": None,
        "description": "Follow-up care balance",
        "balanceOwing": 5000,
        "originalAmount": 5000,
        "reduction": 0,
    })


# ---- Hardening Round 1 ----

def solve_task_h21(state):
    """Find PI matter with most medical providers, add $50K general damage."""
    from collections import Counter
    pi_ids = {m["id"] for m in state["matters"] if m["practiceAreaId"] == "pa_1"}
    counts = Counter()
    for mp in state["medicalProviders"]:
        if mp["matterId"] in pi_ids:
            counts[mp["matterId"]] += 1
    top_matter_id = counts.most_common(1)[0][0]  # matter_1
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": top_matter_id,
        "name": "Long-term disability",
        "amount": 50000,
        "type": "general",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })


def solve_task_h22(state):
    """Newer of two Doyle PI matters: add $5K damage, change attorney to Marcus Williams."""
    doyle_matters = [
        m for m in state["matters"]
        if "doyle" in m["description"].lower() and m["practiceAreaId"] == "pa_1"
    ]
    doyle_matters.sort(key=lambda m: m["openDate"])
    newer = doyle_matters[-1]  # matter_22 (opened 2025-01-20)
    newer["responsibleAttorneyId"] = "user_2"
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": newer["id"],
        "name": "Initial emergency room visit",
        "amount": 5000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })


def solve_task_h23(state):
    """Okafor burn: mark all providers treatment complete, move to Settlement/Trial."""
    m = find_matter_by_desc(state, "Okafor", "burn")
    for mp in state["medicalProviders"]:
        if mp["matterId"] == m["id"]:
            mp["treatmentComplete"] = True
    m["stageId"] = "stage_1_5"


def solve_task_h24(state):
    """Close PI Intake matters opened before January 2025."""
    cutoff = "2025-01-01"
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["stageId"] == "stage_1_1"
                and m["status"] == "open"
                and m.get("openDate", "9999") < cutoff):
            m["status"] = "closed"
            m["closedDate"] = TODAY


def solve_task_h25(state):
    """Chen-Ramirez at Arraignment: change to hourly, budget $15K."""
    m = next(m for m in state["matters"] if m["id"] == "matter_51")
    m["billingMethod"] = "hourly"
    m["billing"]["method"] = "hourly"
    m["billing"]["budget"] = 15000
    m["billing"]["flatRate"] = None


def solve_task_h26(state):
    """Recover two duplicate matters from bin, close them."""
    target_ids = ["del_matter_1", "del_matter_4"]
    for tid in target_ids:
        idx = next(i for i, dm in enumerate(state["deletedMatters"]) if dm["id"] == tid)
        matter = state["deletedMatters"].pop(idx)
        matter["status"] = "closed"
        matter["closedDate"] = TODAY
        state["matters"].append(matter)


def solve_task_h27(state):
    """Find attorney with most CD matters, create CD matter for Thompson."""
    from collections import Counter
    cd_matters = [m for m in state["matters"] if m["practiceAreaId"] == "pa_3"]
    counts = Counter(m["responsibleAttorneyId"] for m in cd_matters)
    top_atty = counts.most_common(1)[0][0]  # user_8
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-Thompson",
        "description": "People v. Thompson - New Criminal Defense Matter",
        "status": "open",
        "billingMethod": "flat_rate",
        "clientId": "contact_9",
        "responsibleAttorneyId": top_atty,
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_3",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "flat_rate", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None,
            "flatRate": {"amount": 8000, "userId": top_atty},
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h28(state):
    """Patterson bus: add Bay Area Ortho relationship + $2500 outstanding balance."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    m.setdefault("relationships", []).append({
        "contactId": "contact_56",
        "relationship": "Medical Provider",
        "billRecipient": False,
    })
    settlement = ensure_settlement(state, m["id"])
    next_id = len(settlement["outstandingBalances"]) + 1
    settlement["outstandingBalances"].append({
        "id": f"ob_{next_id}",
        "responsibility": "client",
        "holderContactId": "contact_56",
        "description": "Bay Area Orthopedic Associates balance",
        "balanceOwing": 2500,
        "originalAmount": 2500,
        "reduction": 0,
    })


def solve_task_h29(state):
    """Transfer Marcus Williams' open PI Investigation matters to Diana Reyes + Demand."""
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["stageId"] == "stage_1_2"
                and m["status"] == "open"
                and m["responsibleAttorneyId"] == "user_2"):
            m["responsibleAttorneyId"] = "user_3"
            m["stageId"] = "stage_1_3"


def solve_task_h30(state):
    """McCarthy chiropractic provider: set record/bill status, first treatment date."""
    m = find_matter_by_desc(state, "McCarthy", "pedestrian")
    for mp in state["medicalProviders"]:
        if mp["matterId"] == m["id"] and mp.get("contactId") == "contact_60":
            mp["recordStatus"] = "received"
            mp["billStatus"] = "received"
            mp["firstTreatmentDate"] = "2024-10-15"


def solve_task_h31(state):
    """Create Securities Law PA with 3 stages, move Franklin case."""
    max_num = max(int(pa["id"].split("_")[1]) for pa in state["practiceAreas"])
    pa_id = f"pa_{max_num + 1}"
    sec_filing_stage_id = f"stage_{max_num + 1}_2"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Securities Law",
        "stages": [
            {"id": f"stage_{max_num + 1}_1", "name": "Investigation", "order": 0},
            {"id": sec_filing_stage_id, "name": "SEC Filing", "order": 1},
            {"id": f"stage_{max_num + 1}_3", "name": "Litigation", "order": 2},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })
    m = find_matter_by_desc(state, "Franklin", "Securities fraud")
    m["practiceAreaId"] = pa_id
    m["stageId"] = sec_filing_stage_id


def solve_task_h32(state):
    """CD Plea Negotiation: pending→open, open→Trial stage."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_3" and m["stageId"] == "stage_3_3":
            if m["status"] == "open":
                m["stageId"] = "stage_3_4"
            elif m["status"] == "pending":
                m["status"] = "open"
                m["pendingDate"] = None


def solve_task_h33(state):
    """Doyle scaffolding settlement: $350K recovery, 33.33% fee, $15K lien, $8.5K balance."""
    m = find_matter_by_desc(state, "Doyle", "scaffolding")
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 350000,
        "sourceContactId": None,
        "sourceName": "Summit Construction Insurance",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": m["responsibleAttorneyId"],
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_58",
        "description": "State Farm Insurance lien",
        "amount": 15000,
        "reduction": 0,
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": "contact_55",
        "description": "SF General Hospital outstanding balance",
        "balanceOwing": 8500,
        "originalAmount": 8500,
        "reduction": 0,
    })


def solve_task_h34(state):
    """Find PA with most open matters, add Appeal stage."""
    from collections import Counter
    counts = Counter()
    for m in state["matters"]:
        if m["status"] == "open":
            counts[m["practiceAreaId"]] += 1
    top_pa_id = counts.most_common(1)[0][0]  # pa_1
    pa = next(p for p in state["practiceAreas"] if p["id"] == top_pa_id)
    pa["stages"].append({
        "id": f"{top_pa_id.replace('pa', 'stage')}_{len(pa['stages']) + 1}",
        "name": "Appeal",
        "order": len(pa["stages"]),
    })


def solve_task_h35(state):
    """Gonzalez divorce (not paternity): add O'Brien notification, restrict to FL Division."""
    m = find_matter_by_desc(state, "Gonzalez", "Divorce")
    m.setdefault("notifications", []).append({
        "userId": "user_4",
        "types": ["matter_updates"],
    })
    m["permissions"] = {
        "type": "specific",
        "userIds": [],
        "groupIds": ["group_2"],
    }


def solve_task_h36(state):
    """RE: close pending, move open Due Diligence to Contract Review."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_4":
            if m["status"] == "pending":
                m["status"] = "closed"
                m["closedDate"] = TODAY
            elif m["status"] == "open" and m["stageId"] == "stage_4_1":
                m["stageId"] = "stage_4_2"


def solve_task_h37(state):
    """Patterson bus: update first provider statuses, add Settlement Documents folder."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    providers = [mp for mp in state["medicalProviders"] if mp["matterId"] == m["id"]]
    if providers:
        providers[0]["recordStatus"] = "certified"
        providers[0]["billStatus"] = "received"
    m.setdefault("documentFolders", []).append({
        "id": f"folder_{m['id'].split('_')[1]}_{len(m.get('documentFolders', [])) + 1}",
        "name": "Settlement Documents",
        "category": "Settlement",
    })


def solve_task_h38(state):
    """Two Simmons PI matters: higher budget→add damage, lower budget→delete."""
    simmons = [
        m for m in state["matters"]
        if "simmons" in m["description"].lower() and m["practiceAreaId"] == "pa_1"
    ]
    simmons.sort(key=lambda m: m.get("billing", {}).get("budget", 0))
    lower = simmons[0]  # matter_19 (budget=20000)
    higher = simmons[-1]  # matter_13 (budget=55000)

    # Add damage to higher budget
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": higher["id"],
        "name": "Pain and suffering",
        "amount": 100000,
        "type": "general",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })

    # Delete lower budget
    idx = next(i for i, x in enumerate(state["matters"]) if x["id"] == lower["id"])
    matter = state["matters"].pop(idx)
    matter["deletedDate"] = NOW
    state["deletedMatters"].append(matter)


def solve_task_h39(state):
    """Create MedMal template, set as firm default."""
    max_num = max(int(t["id"].split("_")[1]) for t in state["matterTemplates"])
    template_id = f"template_{max_num + 1}"
    state["matterTemplates"].append({
        "id": template_id,
        "name": "Medical Malpractice - Standard",
        "isDefault": False,
        "description": "Template for standard medical malpractice cases",
        "practiceAreaId": "pa_12",
        "billable": True,
        "billingMethod": "contingency",
        "deductionOrder": "fees_first",
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })
    state["firmSettings"]["defaultTemplateId"] = template_id


def solve_task_h40(state):
    """Sullivan-Wright: settlement with recovery, fee, lien, balance + deduction order."""
    m = find_matter_by_desc(state, "Sullivan-Wright")
    if m.get("personalInjury") is None:
        m["personalInjury"] = {}
    m["personalInjury"]["deductionOrder"] = "expenses_first"
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 450000,
        "sourceContactId": None,
        "sourceName": "Kaiser Permanente",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": m["responsibleAttorneyId"],
        "rate": 40,
        "percentage": 40,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": None,
        "description": "Health insurance subrogation lien",
        "amount": 35000,
        "reduction": 0,
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": None,
        "description": "Physical therapy outstanding balance",
        "balanceOwing": 12000,
        "originalAmount": 12000,
        "reduction": 0,
    })


# ---- Hardening Round 2 ----

def solve_task_h41(state):
    """Find PI matter with highest total damages, add $300K recovery + 33.33% fee."""
    from collections import defaultdict
    pi_ids = {m["id"] for m in state["matters"] if m["practiceAreaId"] == "pa_1"}
    totals = defaultdict(float)
    for d in state["damages"]:
        if d["matterId"] in pi_ids:
            totals[d["matterId"]] += d["amount"]
    top_matter_id = max(totals, key=totals.get)  # matter_7
    settlement = ensure_settlement(state, top_matter_id)
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 300000,
        "sourceContactId": None,
        "sourceName": "Settlement Recovery",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": "user_2",
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })


def solve_task_h42(state):
    """PI Investigation: damages→Demand, no damages→pending."""
    damage_mids = set(d["matterId"] for d in state["damages"])
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["stageId"] == "stage_1_2"
                and m["status"] == "open"):
            if m["id"] in damage_mids:
                m["stageId"] = "stage_1_3"
            else:
                m["status"] = "pending"
                m["pendingDate"] = TODAY


def solve_task_h43(state):
    """Rename PI-Auto Accident template, change billing to hourly, set as firm default."""
    template = find_template(state, "Personal Injury - Auto Accident")
    template["name"] = "Personal Injury - Motor Vehicle Collision"
    template["billingMethod"] = "hourly"
    state["firmSettings"]["defaultTemplateId"] = template["id"]


def solve_task_h44(state):
    """Find PA with most pending matters, add Administrative Review stage."""
    from collections import Counter
    counts = Counter()
    for m in state["matters"]:
        if m["status"] == "pending":
            counts[m["practiceAreaId"]] += 1
    top_pa_id = counts.most_common(1)[0][0]  # pa_1
    pa = next(p for p in state["practiceAreas"] if p["id"] == top_pa_id)
    pa["stages"].append({
        "id": f"{top_pa_id.replace('pa', 'stage')}_{len(pa['stages']) + 1}",
        "name": "Administrative Review",
        "order": len(pa["stages"]),
    })


def solve_task_h45(state):
    """Williams' open matters: Demand+ PI→Jackson, other→Reyes."""
    advanced_stages = {"stage_1_3", "stage_1_4", "stage_1_5"}
    for m in state["matters"]:
        if m["responsibleAttorneyId"] == "user_2" and m["status"] == "open":
            if m["practiceAreaId"] == "pa_1" and m["stageId"] in advanced_stages:
                m["responsibleAttorneyId"] = "user_8"
            else:
                m["responsibleAttorneyId"] = "user_3"


def solve_task_h46(state):
    """Numbering: slash + 4-digit. Create Tax Law - Audit Defense template."""
    state["numberingScheme"]["separator"] = "/"
    state["numberingScheme"]["numberPadding"] = 4
    max_num = max(int(t["id"].split("_")[1]) for t in state["matterTemplates"])
    state["matterTemplates"].append({
        "id": f"template_{max_num + 1}",
        "name": "Tax Law - Audit Defense",
        "isDefault": False,
        "description": "Template for tax law audit defense matters",
        "practiceAreaId": "pa_11",
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })


def solve_task_h47(state):
    """Create Maritime Law PA with 3 stages, then create matter for Andrew Kim."""
    max_num = max(int(pa["id"].split("_")[1]) for pa in state["practiceAreas"])
    pa_id = f"pa_{max_num + 1}"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Maritime Law",
        "stages": [
            {"id": f"stage_{max_num + 1}_1", "name": "Investigation", "order": 0},
            {"id": f"stage_{max_num + 1}_2", "name": "Filing", "order": 1},
            {"id": f"stage_{max_num + 1}_3", "name": "Arbitration", "order": 2},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-Kim",
        "description": "Kim Maritime Shipping Dispute",
        "status": "open",
        "billingMethod": "hourly",
        "clientId": "contact_43",
        "responsibleAttorneyId": "user_1",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": pa_id,
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "hourly", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h48(state):
    """Gonzalez divorce settlement: $175K recovery, 25% fee, $12K child support lien."""
    m = find_matter_by_desc(state, "Gonzalez", "Divorce")
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 175000,
        "sourceContactId": None,
        "sourceName": "Divorce settlement",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": m["responsibleAttorneyId"],
        "rate": 25,
        "percentage": 25,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": None,
        "description": "Child support lien",
        "amount": 12000,
        "reduction": 0,
    })


def solve_task_h49(state):
    """Most recently opened PI matter: add $30K special damage, move to Investigation."""
    pi_open = [
        m for m in state["matters"]
        if m["practiceAreaId"] == "pa_1" and m.get("openDate")
    ]
    most_recent = max(pi_open, key=lambda m: m["openDate"])
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": most_recent["id"],
        "name": "Emergency medical treatment",
        "amount": 30000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })
    most_recent["stageId"] = "stage_1_2"


def solve_task_h50(state):
    """Add $10K State Farm lien to every open PI Demand matter's settlement."""
    for m in state["matters"]:
        if (m["practiceAreaId"] == "pa_1"
                and m["stageId"] == "stage_1_3"
                and m["status"] == "open"):
            settlement = ensure_settlement(state, m["id"])
            settlement["nonMedicalLiens"].append({
                "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
                "holderContactId": "contact_58",
                "description": "State Farm Insurance lien",
                "amount": 10000,
                "reduction": 0,
            })


def solve_task_h51(state):
    """Matters opened before June 2024: PI→Settlement/Trial, FL→close."""
    cutoff = "2024-06-01"
    for m in state["matters"]:
        if m["status"] == "open" and m.get("openDate", "9999") < cutoff:
            if m["practiceAreaId"] == "pa_1":
                m["stageId"] = "stage_1_5"
            elif m["practiceAreaId"] == "pa_2":
                m["status"] = "closed"
                m["closedDate"] = TODAY


def solve_task_h52(state):
    """Brennan hotel: Investigation stage, Judge Assigned, $200K recovery."""
    m = find_matter_by_desc(state, "Brennan", "Oceanview")
    m["stageId"] = "stage_1_2"
    m.setdefault("customFields", {})["cf_7"] = "Hon. Michael Rodriguez"
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 200000,
        "sourceContactId": None,
        "sourceName": "Hotel insurance settlement",
    })


def solve_task_h53(state):
    """Ababio PG&E: SF General provider, Court Case Number, $250K recovery."""
    m = find_matter_by_desc(state, "Ababio", "Pacific Gas")
    pid = next_provider_id(state)
    state["medicalProviders"].append({
        "id": f"mp_{pid}",
        "matterId": m["id"],
        "contactId": "contact_55",
        "description": "SF General Hospital emergency treatment",
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
    m.setdefault("customFields", {})["cf_1"] = "SF-2024-PI-8821"
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 250000,
        "sourceContactId": None,
        "sourceName": "PG&E liability settlement",
    })


def solve_task_h54(state):
    """Mills motorcycle: Diana Reyes, contingency 35%, $175K recovery."""
    m = find_matter_by_desc(state, "Mills", "Rodriguez")
    m["responsibleAttorneyId"] = "user_3"
    m["billingMethod"] = "contingency"
    m["billing"]["method"] = "contingency"
    m["billing"]["contingencyFee"] = {"userId": "user_3", "percentage": 35}
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 175000,
        "sourceContactId": None,
        "sourceName": "Insurance settlement",
    })


def solve_task_h55(state):
    """Delete FL-Divorce template, create FL-Dissolution, set as firm default."""
    state["matterTemplates"] = [
        t for t in state["matterTemplates"]
        if t["name"] != "Family Law - Divorce"
    ]
    max_num = max(int(t["id"].split("_")[1]) for t in state["matterTemplates"])
    template_id = f"template_{max_num + 1}"
    state["matterTemplates"].append({
        "id": template_id,
        "name": "Family Law - Dissolution",
        "isDefault": False,
        "description": "Template for family law dissolution matters",
        "practiceAreaId": "pa_2",
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })
    state["firmSettings"]["defaultTemplateId"] = template_id


def solve_task_h56(state):
    """Whitfield BART: contingency 40%, custom fields, Investigation stage."""
    m = find_matter_by_desc(state, "Whitfield", "Bay Area Rapid Transit")
    m["billingMethod"] = "contingency"
    m["billing"]["method"] = "contingency"
    m["billing"]["contingencyFee"] = {"userId": m["responsibleAttorneyId"], "percentage": 40}
    m.setdefault("customFields", {})["cf_1"] = "SF-2025-PI-1212"
    m["customFields"]["cf_7"] = "Hon. Patricia Chen"
    m["stageId"] = "stage_1_2"


def solve_task_h57(state):
    """Doyle scaffolding + Mills motorcycle: $5K outstanding balance each."""
    for desc_kws in [("Doyle", "Summit"), ("Mills", "Rodriguez")]:
        m = find_matter_by_desc(state, *desc_kws)
        settlement = ensure_settlement(state, m["id"])
        settlement["outstandingBalances"].append({
            "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
            "responsibility": "client",
            "holderContactId": "contact_57",
            "description": "Pacific Physical Therapy Center balance",
            "balanceOwing": 5000,
            "originalAmount": 5000,
            "reduction": 0,
        })


def solve_task_h58(state):
    """Create new PI matter for Angela Dimitriou with contingency + folder."""
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-Dimitriou",
        "description": "Dimitriou v. City of Oakland - Sidewalk fall",
        "status": "open",
        "billingMethod": "contingency",
        "clientId": "contact_53",
        "responsibleAttorneyId": "user_3",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_1",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "contingency", "currency": "USD",
            "rates": [], "budget": 0, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0,
            "contingencyFee": {"userId": "user_3", "percentage": 33.33},
            "flatRate": None,
        },
        "personalInjury": {"deductionOrder": "fees_first"},
        "notifications": [],
        "documentFolders": [
            {"id": f"folder_{mid}_1", "name": "Incident Photos", "category": "Evidence"},
        ],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h59(state):
    """Open EL matters: Intake→EEOC, Negotiation→Litigation."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_6" and m["status"] == "open":
            if m["stageId"] == "stage_6_1":
                m["stageId"] = "stage_6_2"
            elif m["stageId"] == "stage_6_3":
                m["stageId"] = "stage_6_4"


def solve_task_h60(state):
    """Washington: CAD currency, UCSF related contact, $30K CalComp lien."""
    m = find_matter_by_desc(state, "Washington", "Pacific Steel")
    m["billing"]["currency"] = "CAD"
    m.setdefault("relationships", []).append({
        "contactId": "contact_59",
        "relationship": "Medical Provider",
        "billRecipient": False,
    })
    settlement = ensure_settlement(state, m["id"])
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_42",
        "description": "CalComp Workers Compensation lien",
        "amount": 30000,
        "reduction": 0,
    })


# ---- Hardening Round 3 ----

def solve_task_h61(state):
    """Matter with most billable hours -> pending + Court Case Number."""
    hours_by_matter = {}
    for te in state["timeEntries"]:
        mid = te["matterId"]
        hours_by_matter[mid] = hours_by_matter.get(mid, 0) + te["hours"]
    top_matter_id = max(hours_by_matter, key=hours_by_matter.get)  # matter_94
    m = find_matter_by_id(state, top_matter_id)
    m["status"] = "pending"
    m["pendingDate"] = TODAY
    m.setdefault("customFields", {})["cf_1"] = "HIGH-PRIORITY-2026"


def solve_task_h62(state):
    """Patterson bus: total medical bill balance -> non-medical lien from State Farm."""
    m = find_matter_by_desc(state, "Patterson", "Metro Transit")
    total_balance = sum(
        b.get("balanceOwed", 0)
        for b in state["medicalBills"]
        if b["matterId"] == m["id"]
    )  # 5250 + 4200 + 3200 + 1200 = 13850
    settlement = ensure_settlement(state, m["id"])
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_58",
        "description": "State Farm Insurance lien",
        "amount": total_balance,
        "reduction": 0,
    })


def solve_task_h63(state):
    """Priya Sharma caseload: contingency -> Williams, other -> Jackson."""
    for m in state["matters"]:
        if m["responsibleAttorneyId"] == "user_5" and m["status"] == "open":
            if m["billingMethod"] == "contingency":
                m["responsibleAttorneyId"] = "user_2"
            else:
                m["responsibleAttorneyId"] = "user_8"


def solve_task_h64(state):
    """Create Admiralty Law PA -> template -> matter for Pacific Rim."""
    max_pa = max(int(pa["id"].split("_")[1]) for pa in state["practiceAreas"])
    pa_id = f"pa_{max_pa + 1}"
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Admiralty Law",
        "stages": [
            {"id": f"stage_{max_pa + 1}_1", "name": "Pre-Filing", "order": 0},
            {"id": f"stage_{max_pa + 1}_2", "name": "Discovery", "order": 1},
            {"id": f"stage_{max_pa + 1}_3", "name": "Trial", "order": 2},
        ],
        "color": "#6366f1",
        "createdDate": NOW,
    })
    max_t = max(int(t["id"].split("_")[1]) for t in state["matterTemplates"])
    state["matterTemplates"].append({
        "id": f"template_{max_t + 1}",
        "name": "Admiralty - Cargo Dispute",
        "isDefault": False,
        "description": "Template for admiralty cargo dispute matters",
        "practiceAreaId": pa_id,
        "billable": True,
        "billingMethod": "hourly",
        "deductionOrder": None,
        "customFields": {},
        "documentFolders": [],
        "createdDate": NOW,
    })
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-PacificRim",
        "description": "Pacific Rim Imports - Admiralty Cargo Dispute",
        "status": "open",
        "billingMethod": "hourly",
        "clientId": "contact_10",
        "responsibleAttorneyId": "user_16",
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": pa_id,
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "hourly", "currency": "USD",
            "rates": [], "budget": 60000, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h65(state):
    """PA with highest total open-matter budget -> add Financial Review stage."""
    budget_by_pa = {}
    for m in state["matters"]:
        if m["status"] != "open":
            continue
        pa_id = m["practiceAreaId"]
        budget = m.get("billing", {}).get("budget", 0)
        budget_by_pa[pa_id] = budget_by_pa.get(pa_id, 0) + budget
    top_pa_id = max(budget_by_pa, key=budget_by_pa.get)  # pa_1
    pa = next(p for p in state["practiceAreas"] if p["id"] == top_pa_id)
    pa["stages"].append({
        "id": f"{top_pa_id.replace('pa', 'stage')}_{len(pa['stages']) + 1}",
        "name": "Financial Review",
        "order": len(pa["stages"]),
    })


def solve_task_h66(state):
    """Fitzgerald med mal case: set 4 custom fields."""
    m = find_matter_by_desc(state, "Fitzgerald", "Misdiagnosis")
    m.setdefault("customFields", {})
    m["customFields"]["cf_1"] = "SF-2025-MM-7734"
    m["customFields"]["cf_7"] = "Hon. Richard Alvarez"
    m["customFields"]["cf_4"] = "Kaiser Permanente"
    m["customFields"]["cf_5"] = 1000000


def solve_task_h67(state):
    """Duplicate Patterson bus accident, then modify the copy."""
    original = find_matter_by_desc(state, "Patterson", "Metro Transit")
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    dup = deepcopy(original)
    dup["id"] = f"matter_{mid}"
    dup["number"] = number
    dup["displayNumber"] = f"{number}-Patterson"
    dup["description"] = "Patterson v. Metro Transit Authority - Supplemental claim"
    dup["responsibleAttorneyId"] = "user_3"
    dup["billingMethod"] = "hourly"
    dup["billing"]["method"] = "hourly"
    dup["billing"]["contingencyFee"] = None
    dup["billing"]["budget"] = 25000
    dup["billing"]["budgetUsed"] = 0
    dup["createdDate"] = NOW
    state["matters"].append(dup)


def solve_task_h68(state):
    """Doyle scaffolding: $20K damage + Bay Area Ortho provider + $100K recovery."""
    m = find_matter_by_desc(state, "Doyle", "Summit")
    did = next_damage_id(state)
    state["damages"].append({
        "id": f"dmg_{did}",
        "matterId": m["id"],
        "name": "Shoulder surgery",
        "amount": 20000,
        "type": "special",
        "date": None,
        "notes": "",
        "createdDate": NOW,
        "updatedDate": NOW,
    })
    pid = next_provider_id(state)
    state["medicalProviders"].append({
        "id": f"mp_{pid}",
        "matterId": m["id"],
        "contactId": "contact_56",
        "description": "Bay Area Orthopedic Associates orthopedic care",
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
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 100000,
        "sourceContactId": None,
        "sourceName": "Summit Construction Insurance",
    })


def solve_task_h69(state):
    """Top originating attorney -> new Corporate matter for Redwood Financial."""
    from collections import Counter
    counts = Counter()
    for m in state["matters"]:
        if m["status"] == "open" and m.get("originatingAttorneyId"):
            counts[m["originatingAttorneyId"]] += 1
    top_atty = counts.most_common(1)[0][0]  # user_1
    mid = next_matter_id(state)
    number = str(mid).zfill(5)
    state["matters"].append({
        "id": f"matter_{mid}",
        "number": number,
        "displayNumber": f"{number}-RedwoodFinancial",
        "description": "Redwood Financial Services - Corporate Advisory",
        "status": "open",
        "billingMethod": "hourly",
        "clientId": "contact_38",
        "responsibleAttorneyId": top_atty,
        "originatingAttorneyId": top_atty,
        "responsibleStaffId": None,
        "clientReferenceNumber": "",
        "location": "",
        "practiceAreaId": "pa_5",
        "stageId": None,
        "openDate": TODAY,
        "pendingDate": None,
        "closedDate": None,
        "createdDate": NOW,
        "templateId": None,
        "permissions": {"type": "everyone", "userIds": [], "groupIds": []},
        "blockedUsers": [],
        "relationships": [],
        "customFields": {},
        "billing": {
            "billable": True, "method": "hourly", "currency": "USD",
            "rates": [], "budget": 40000, "budgetUsed": 0, "trustBalance": 0,
            "minimumTrust": 0, "contingencyFee": None, "flatRate": None,
        },
        "personalInjury": None,
        "notifications": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingPct": 50, "responsiblePct": 50},
        "deleted": False, "deletedAt": None,
    })


def solve_task_h70(state):
    """Recover Test Matter, Template Matter, Jones inquiry from bin -> close all."""
    target_ids = ["del_matter_2", "del_matter_5", "del_matter_6"]
    for tid in target_ids:
        idx = next(i for i, dm in enumerate(state["deletedMatters"]) if dm["id"] == tid)
        matter = state["deletedMatters"].pop(idx)
        matter["status"] = "closed"
        matter["closedDate"] = TODAY
        state["matters"].append(matter)


def solve_task_h71(state):
    """Chen-Ramirez Amazon: 5-item settlement setup + deduction order."""
    m = find_matter_by_desc(state, "Chen-Ramirez", "Amazon")
    if m.get("personalInjury") is None:
        m["personalInjury"] = {}
    m["personalInjury"]["deductionOrder"] = "expenses_first"
    settlement = ensure_settlement(state, m["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 180000,
        "sourceContactId": None,
        "sourceName": "Insurance settlement",
    })
    settlement["legalFees"].append({
        "id": f"lf_{len(settlement['legalFees']) + 1}",
        "recoveryId": None,
        "recipientId": m["responsibleAttorneyId"],
        "rate": 33.33,
        "percentage": 33.33,
        "flatAmount": 0,
        "discount": 0,
        "referralFees": [],
    })
    settlement["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_30",
        "description": "ABC Insurance Co. lien",
        "amount": 12000,
        "reduction": 0,
    })
    settlement["outstandingBalances"].append({
        "id": f"ob_{len(settlement['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": "contact_55",
        "description": "SF General Hospital balance",
        "balanceOwing": 4500,
        "originalAmount": 4500,
        "reduction": 0,
    })


def solve_task_h72(state):
    """Earliest open PI Litigation matter: $150K recovery + Settlement/Trial stage."""
    pi_lit = [
        m for m in state["matters"]
        if m["practiceAreaId"] == "pa_1"
        and m["stageId"] == "stage_1_4"
        and m["status"] == "open"
        and m.get("openDate")
    ]
    earliest = min(pi_lit, key=lambda m: m["openDate"])  # matter_4
    settlement = ensure_settlement(state, earliest["id"])
    settlement["recoveries"].append({
        "id": f"rec_{len(settlement['recoveries']) + 1}",
        "amount": 150000,
        "sourceContactId": None,
        "sourceName": "Settlement recovery",
    })
    earliest["stageId"] = "stage_1_5"


def solve_task_h73(state):
    """Johnson v. Whole Foods, UCSF provider: add medical record + bill."""
    m = find_matter_by_desc(state, "Johnson", "Whole Foods")
    # Find UCSF provider (mp_4)
    ucsf = next(
        p for p in state["medicalProviders"]
        if p["matterId"] == m["id"] and p["contactId"] == "contact_59"
    )
    # Add medical record
    mr_id = state.get("_nextMedicalRecordId", 16)
    state["_nextMedicalRecordId"] = mr_id + 1
    state["medicalRecords"].append({
        "id": f"mr_{mr_id}",
        "providerId": ucsf["id"],
        "matterId": m["id"],
        "type": "office_visit",
        "date": "2025-03-15",
        "description": "Follow-up MRI scan",
        "status": "received",
        "requestedDate": None,
        "receivedDate": "2025-03-15",
    })
    # Add medical bill
    mb_id = state.get("_nextMedicalBillId", 16)
    state["_nextMedicalBillId"] = mb_id + 1
    state["medicalBills"].append({
        "id": f"mb_{mb_id}",
        "providerId": ucsf["id"],
        "matterId": m["id"],
        "fileName": "Invoice_UCSF_MRI_March2025.pdf",
        "billDate": "2025-03-15",
        "receivedDate": "2025-03-15",
        "billAmount": 3500,
        "adjustment": 0,
        "payers": [],
        "balanceOwed": 3500,
        "balanceLien": False,
        "outstandingBalance": True,
        "status": "outstanding",
    })


def solve_task_h74(state):
    """Add Pacific Physical Therapy to Doyle scaffolding + Washington crush injury."""
    m1 = find_matter_by_desc(state, "Doyle", "Summit")
    m2 = find_matter_by_desc(state, "Washington", "Pacific Steel")
    for m in [m1, m2]:
        pid = next_provider_id(state)
        state["medicalProviders"].append({
            "id": f"mp_{pid}",
            "matterId": m["id"],
            "contactId": "contact_57",
            "description": "Pacific Physical Therapy Center rehabilitation",
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


def solve_task_h75(state):
    """Two PI Litigation matters: earlier -> $15K balance, later -> $10K lien."""
    pi_lit = [
        m for m in state["matters"]
        if m["practiceAreaId"] == "pa_1"
        and m["stageId"] == "stage_1_4"
        and m["status"] == "open"
        and m.get("openDate")
    ]
    pi_lit.sort(key=lambda m: m["openDate"])
    earlier = pi_lit[0]   # matter_4 (Washington, 2024-04-20)
    later = pi_lit[-1]    # matter_7 (Okafor, 2024-07-22)

    settlement_e = ensure_settlement(state, earlier["id"])
    settlement_e["outstandingBalances"].append({
        "id": f"ob_{len(settlement_e['outstandingBalances']) + 1}",
        "responsibility": "client",
        "holderContactId": "contact_57",
        "description": "Pacific Physical Therapy Center balance",
        "balanceOwing": 15000,
        "originalAmount": 15000,
        "reduction": 0,
    })

    settlement_l = ensure_settlement(state, later["id"])
    settlement_l["nonMedicalLiens"].append({
        "id": f"nml_{len(settlement_l['nonMedicalLiens']) + 1}",
        "holderContactId": "contact_30",
        "description": "ABC Insurance Co. lien",
        "amount": 10000,
        "reduction": 0,
    })


def solve_task_h76(state):
    """Top 3 PI matters by damage total: add $10K State Farm lien to each."""
    from collections import defaultdict
    pi_ids = {m["id"] for m in state["matters"] if m["practiceAreaId"] == "pa_1"}
    totals = defaultdict(float)
    for d in state["damages"]:
        if d["matterId"] in pi_ids:
            totals[d["matterId"]] += d["amount"]
    sorted_matters = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    top_3 = [mid for mid, _ in sorted_matters[:3]]
    for mid in top_3:
        settlement = ensure_settlement(state, mid)
        settlement["nonMedicalLiens"].append({
            "id": f"nml_{len(settlement['nonMedicalLiens']) + 1}",
            "holderContactId": "contact_58",
            "description": "State Farm Insurance lien",
            "amount": 10000,
            "reduction": 0,
        })


def solve_task_h77(state):
    """Okafor burn: restrict to Litigation Team, block Cooper, add notif recipients."""
    m = find_matter_by_desc(state, "Okafor", "HomeComfort")
    m["permissions"] = {
        "type": "specific",
        "userIds": [],
        "groupIds": ["group_1"],
    }
    m.setdefault("blockedUsers", []).append("user_14")
    m.setdefault("notifications", []).extend([
        {"userId": "user_6", "types": ["matter_updates"]},
        {"userId": "user_9", "types": ["matter_updates"]},
    ])


def solve_task_h78(state):
    """EP matters: Initial Consultation -> Doc Prep, Doc Prep -> Execution."""
    for m in state["matters"]:
        if m["practiceAreaId"] == "pa_7" and m["status"] == "open":
            if m["stageId"] == "stage_7_1":
                m["stageId"] = "stage_7_2"
            elif m["stageId"] == "stage_7_2":
                m["stageId"] = "stage_7_3"


def solve_task_h79(state):
    """McCarthy pedestrian: delete all providers + records/bills, add UCSF + Horizon."""
    m = find_matter_by_desc(state, "McCarthy", "pedestrian")
    old_prov_ids = {
        p["id"] for p in state["medicalProviders"] if p["matterId"] == m["id"]
    }
    state["medicalProviders"] = [
        p for p in state["medicalProviders"]
        if p["id"] not in old_prov_ids
    ]
    state["medicalRecords"] = [
        r for r in state["medicalRecords"]
        if r["providerId"] not in old_prov_ids
    ]
    state["medicalBills"] = [
        b for b in state["medicalBills"]
        if b["providerId"] not in old_prov_ids
    ]
    for contact_id, desc in [
        ("contact_59", "UCSF Medical Center treatment"),
        ("contact_68", "Horizon Healthcare Partners treatment"),
    ]:
        pid = next_provider_id(state)
        state["medicalProviders"].append({
            "id": f"mp_{pid}",
            "matterId": m["id"],
            "contactId": contact_id,
            "description": desc,
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


def solve_task_h80(state):
    """Add Emergency Filing stage to PI and Medical Malpractice."""
    for pa_id in ["pa_1", "pa_12"]:
        pa = next(p for p in state["practiceAreas"] if p["id"] == pa_id)
        pa["stages"].append({
            "id": f"{pa_id.replace('pa', 'stage')}_{len(pa['stages']) + 1}",
            "name": "Emergency Filing",
            "order": len(pa["stages"]),
        })


# ---------------------------------------------------------------------------
# SOLVERS dispatch map
# ---------------------------------------------------------------------------
SOLVERS = {
    "task_e1": solve_task_e1, "task_e2": solve_task_e2, "task_e3": solve_task_e3,
    "task_e4": solve_task_e4, "task_e5": solve_task_e5, "task_e6": solve_task_e6,
    "task_e7": solve_task_e7, "task_e8": solve_task_e8, "task_e9": solve_task_e9,
    "task_e10": solve_task_e10, "task_e11": solve_task_e11, "task_e12": solve_task_e12,
    "task_e13": solve_task_e13, "task_e14": solve_task_e14, "task_e15": solve_task_e15,
    "task_e16": solve_task_e16, "task_e17": solve_task_e17, "task_e18": solve_task_e18,
    "task_e19": solve_task_e19, "task_e20": solve_task_e20,
    "task_m1": solve_task_m1, "task_m2": solve_task_m2, "task_m3": solve_task_m3,
    "task_m4": solve_task_m4, "task_m5": solve_task_m5, "task_m6": solve_task_m6,
    "task_m7": solve_task_m7, "task_m8": solve_task_m8, "task_m9": solve_task_m9,
    "task_m10": solve_task_m10, "task_m11": solve_task_m11, "task_m12": solve_task_m12,
    "task_m13": solve_task_m13, "task_m14": solve_task_m14, "task_m15": solve_task_m15,
    "task_m16": solve_task_m16, "task_m17": solve_task_m17, "task_m18": solve_task_m18,
    "task_m19": solve_task_m19, "task_m20": solve_task_m20,
    "task_h1": solve_task_h1, "task_h2": solve_task_h2, "task_h3": solve_task_h3,
    "task_h4": solve_task_h4, "task_h5": solve_task_h5, "task_h6": solve_task_h6,
    "task_h7": solve_task_h7, "task_h8": solve_task_h8, "task_h9": solve_task_h9,
    "task_h10": solve_task_h10, "task_h11": solve_task_h11, "task_h12": solve_task_h12,
    "task_h13": solve_task_h13, "task_h14": solve_task_h14, "task_h15": solve_task_h15,
    "task_h16": solve_task_h16, "task_h17": solve_task_h17, "task_h18": solve_task_h18,
    "task_h19": solve_task_h19, "task_h20": solve_task_h20,
    "task_h21": solve_task_h21, "task_h22": solve_task_h22, "task_h23": solve_task_h23,
    "task_h24": solve_task_h24, "task_h25": solve_task_h25, "task_h26": solve_task_h26,
    "task_h27": solve_task_h27, "task_h28": solve_task_h28, "task_h29": solve_task_h29,
    "task_h30": solve_task_h30, "task_h31": solve_task_h31, "task_h32": solve_task_h32,
    "task_h33": solve_task_h33, "task_h34": solve_task_h34, "task_h35": solve_task_h35,
    "task_h36": solve_task_h36, "task_h37": solve_task_h37, "task_h38": solve_task_h38,
    "task_h39": solve_task_h39, "task_h40": solve_task_h40,
    "task_h41": solve_task_h41, "task_h42": solve_task_h42, "task_h43": solve_task_h43,
    "task_h44": solve_task_h44, "task_h45": solve_task_h45, "task_h46": solve_task_h46,
    "task_h47": solve_task_h47, "task_h48": solve_task_h48, "task_h49": solve_task_h49,
    "task_h50": solve_task_h50, "task_h51": solve_task_h51, "task_h52": solve_task_h52,
    "task_h53": solve_task_h53, "task_h54": solve_task_h54, "task_h55": solve_task_h55,
    "task_h56": solve_task_h56, "task_h57": solve_task_h57, "task_h58": solve_task_h58,
    "task_h59": solve_task_h59, "task_h60": solve_task_h60,
    "task_h61": solve_task_h61, "task_h62": solve_task_h62, "task_h63": solve_task_h63,
    "task_h64": solve_task_h64, "task_h65": solve_task_h65, "task_h66": solve_task_h66,
    "task_h67": solve_task_h67, "task_h68": solve_task_h68, "task_h69": solve_task_h69,
    "task_h70": solve_task_h70, "task_h71": solve_task_h71, "task_h72": solve_task_h72,
    "task_h73": solve_task_h73, "task_h74": solve_task_h74, "task_h75": solve_task_h75,
    "task_h76": solve_task_h76, "task_h77": solve_task_h77, "task_h78": solve_task_h78,
    "task_h79": solve_task_h79, "task_h80": solve_task_h80,
}


# ---------------------------------------------------------------------------
# Server management
# ---------------------------------------------------------------------------
def kill_port(port):
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True,
        )
        for pid in result.stdout.strip().split("\n"):
            if pid:
                os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass


def start_server(port):
    kill_port(port)
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def wait_for_server(port, timeout=10):
    url = f"http://localhost:{port}/api/state"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code in (200, 404):
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.2)
    return False


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


# ---------------------------------------------------------------------------
# Verifier loader
# ---------------------------------------------------------------------------
def load_verifier(task):
    path = str(APP_DIR / task["verify"])
    spec = importlib.util.spec_from_file_location(task["id"], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


# ---------------------------------------------------------------------------
# Task runner
# ---------------------------------------------------------------------------
def run_single_task(task, server_url, seed_state):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver for {task_id}"

    # 1. Reset via POST /api/reset
    try:
        requests.post(f"{server_url}/api/reset", timeout=5)
        time.sleep(0.3)
    except Exception as e:
        return task_id, False, f"Reset failed: {e}"

    # 2. Seed the server
    state = deepcopy(seed_state)
    try:
        requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
    except Exception as e:
        return task_id, False, f"Seed failed: {e}"

    # 3. Apply solve
    try:
        solver(state)
    except Exception as e:
        return task_id, False, f"Solve error: {e}"

    # 4. Push solved state
    try:
        requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
    except Exception as e:
        return task_id, False, f"Push state failed: {e}"

    # 5. Run verifier
    try:
        verify_fn = load_verifier(task)
        passed, message = verify_fn(server_url)
    except Exception as e:
        return task_id, False, f"Verifier exception: {e}"

    return task_id, passed, message


def run_tasks_sequential(tasks, port, seed_state):
    proc = start_server(port)
    if not wait_for_server(port):
        stop_server(proc)
        print(f"FATAL: Server on port {port} did not start.", file=sys.stderr)
        sys.exit(1)

    server_url = f"http://localhost:{port}"

    # Seed initial state so server has _seed_state
    requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    results = []
    for task in tasks:
        tid, passed, msg = run_single_task(task, server_url, seed_state)
        status = "\033[92m  PASS\033[0m" if passed else "\033[91m  FAIL\033[0m"
        print(f"{status}  {tid:12s}  {msg}")
        results.append((tid, passed, msg))

    stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    results = []

    def worker_fn(worker_tasks, port):
        proc = start_server(port)
        if not wait_for_server(port):
            stop_server(proc)
            return [(t["id"], False, "Server failed to start") for t in worker_tasks]

        server_url = f"http://localhost:{port}"
        requests.put(
            f"{server_url}/api/state",
            json=seed_state,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

        worker_results = []
        for task in worker_tasks:
            tid, passed, msg = run_single_task(task, server_url, seed_state)
            worker_results.append((tid, passed, msg))
        stop_server(proc)
        return worker_results

    # Partition tasks across workers
    partitions = [[] for _ in range(workers)]
    for i, task in enumerate(tasks):
        partitions[i % workers].append(task)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for w, partition in enumerate(partitions):
            if partition:
                f = executor.submit(worker_fn, partition, base_port + w)
                futures[f] = w

        for f in as_completed(futures):
            for tid, passed, msg in f.result():
                status = "\033[92m  PASS\033[0m" if passed else "\033[91m  FAIL\033[0m"
                print(f"{status}  {tid:12s}  {msg}")
                results.append((tid, passed, msg))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Sanity check for Clio Matters real tasks")
    parser.add_argument("--task-id", help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    # Load tasks
    with open(TASKS_FILE) as f:
        tasks = json.load(f)

    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"ERROR: Task {args.task_id!r} not found.", file=sys.stderr)
            sys.exit(1)

    # Generate seed state
    print("Generating seed state from data.js...")
    seed_state = generate_seed_state()
    print(f"Seed state loaded: {len(seed_state['matters'])} matters, "
          f"{len(seed_state['damages'])} damages, "
          f"{len(seed_state['medicalProviders'])} providers\n")

    # Run tasks
    if args.workers > 1 and len(tasks) > 1:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)
    else:
        results = run_tasks_sequential(tasks, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [(tid, msg) for tid, p, msg in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print("Failed:")
        for tid, msg in failed:
            print(f"  {tid}: {msg}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
