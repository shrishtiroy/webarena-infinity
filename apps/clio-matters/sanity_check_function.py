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

const state = {
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    firmUsers: JSON.parse(JSON.stringify(FIRM_USERS)),
    userGroups: JSON.parse(JSON.stringify(USER_GROUPS)),
    practiceAreas: JSON.parse(JSON.stringify(PRACTICE_AREAS)),
    matterStages: JSON.parse(JSON.stringify(MATTER_STAGES)),
    contacts: JSON.parse(JSON.stringify(CONTACTS)),
    customFieldDefinitions: JSON.parse(JSON.stringify(CUSTOM_FIELD_DEFINITIONS)),
    taskLists: JSON.parse(JSON.stringify(TASK_LISTS)),
    documentCategories: [...DOCUMENT_CATEGORIES],
    currencies: [...CURRENCIES],
    locations: [...LOCATIONS],
    damageTypes: JSON.parse(JSON.stringify(DAMAGE_TYPES)),
    expenseCategories: [...EXPENSE_CATEGORIES],
    matterTemplates: JSON.parse(JSON.stringify(MATTER_TEMPLATES)),
    numberingScheme: JSON.parse(JSON.stringify(NUMBERING_SCHEME)),
    matters: JSON.parse(JSON.stringify(MATTERS)),
    deletedMatters: JSON.parse(JSON.stringify(DELETED_MATTERS)),
    _seedVersion: SEED_DATA_VERSION,
    _nextIds: { matter: 147, contact: 29, damage: 100, recovery: 20, legalFee: 20, lien: 10, balance: 10, medProvider: 50, medRecord: 50, medBill: 50, comment: 20, template: 6, practiceArea: 15, stage: 30, timeline: 200 }
};
process.stdout.write(JSON.stringify(state));
"""


# -- helpers ----------------------------------------------------------------

def find_entity(entities, **kwargs):
    """Find an entity by attribute match. Raises if not found."""
    for e in entities:
        if all(e.get(k) == v for k, v in kwargs.items()):
            return e
    raise ValueError(f"Entity not found: {kwargs}")


def find_matter(state, desc_fragment):
    """Find a matter whose description contains the fragment."""
    for m in state["matters"]:
        if desc_fragment in m["description"]:
            return m
    raise ValueError(f"Matter not found containing: {desc_fragment!r}")


def find_contact_by_name(state, name):
    """Find a contact by lastName (companies) or full name (persons)."""
    for c in state["contacts"]:
        if c["type"] == "company" and c["lastName"] == name:
            return c
        if c["type"] == "person" and f"{c['firstName']} {c['lastName']}" == name:
            return c
        if c["lastName"] == name:
            return c
    raise ValueError(f"Contact not found: {name!r}")


def find_user_by_name(state, name):
    """Find a firm user by fullName."""
    for u in state["firmUsers"]:
        if u["fullName"] == name:
            return u
    raise ValueError(f"User not found: {name!r}")


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


def find_provider(matter, contact_id):
    """Find a medical provider by contactId within a matter."""
    for p in matter["medicalProviders"]:
        if p["contactId"] == contact_id:
            return p
    raise ValueError(f"Provider not found with contactId: {contact_id!r}")


def find_record(provider, file_name):
    """Find a medical record by fileName within a provider."""
    for r in provider["medicalRecords"]:
        if r["fileName"] == file_name:
            return r
    raise ValueError(f"Record not found: {file_name!r}")


def find_bill(provider, file_name):
    """Find a medical bill by fileName within a provider."""
    for b in provider["medicalBills"]:
        if b["fileName"] == file_name:
            return b
    raise ValueError(f"Bill not found: {file_name!r}")


def gen_id(state, id_type):
    """Generate the next ID for a given type, incrementing the counter."""
    n = state["_nextIds"][id_type]
    state["_nextIds"][id_type] = n + 1
    return n


# -- solve functions --------------------------------------------------------

def solve_task_1(state):
    """Change status of Rodriguez v. Premier Auto to Pending."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["status"] = "Pending"
    if not m.get("pendingDate"):
        m["pendingDate"] = "2026-03-07T00:00:00Z"


def solve_task_2(state):
    """Change status of Nguyen Divorce from Pending to Closed."""
    m = find_matter(state, "Nguyen - Divorce")
    m["status"] = "Closed"
    if not m.get("closedDate"):
        m["closedDate"] = "2026-03-07T00:00:00Z"


def solve_task_3(state):
    """Reopen Midwest Manufacturing (Closed -> Open)."""
    m = find_matter(state, "Midwest Manufacturing")
    m["status"] = "Open"
    m["closedDate"] = None


def solve_task_4(state):
    """Delete Baker - Residential Property Purchase."""
    idx = next(i for i, m in enumerate(state["matters"]) if "Baker" in m["description"] and "Residential" in m["description"])
    m = state["matters"].pop(idx)
    state["deletedMatters"].append({
        "id": m["id"],
        "matterNumber": m["matterNumber"],
        "displayNumber": m["displayNumber"],
        "description": m["description"],
        "clientId": m["clientId"],
        "contactName": m["contactName"],
        "deletedAt": "2026-03-07T00:00:00Z",
        "deletedBy": state["currentUser"]["id"],
        "canRecover": True,
    })


def solve_task_5(state):
    """Duplicate Cruz v. Metro Transit."""
    orig = find_matter(state, "Cruz v. Metro Transit")
    clone = deepcopy(orig)
    num = str(gen_id(state, "matter")).zfill(5)
    clone["id"] = "mat_" + num
    clone["matterNumber"] = num
    last_name = clone["contactName"].split()[-1]
    clone["displayNumber"] = num + "-" + last_name
    clone["createdAt"] = "2026-03-07T00:00:00Z"
    clone["updatedAt"] = "2026-03-07T00:00:00Z"
    clone["timeline"] = [{
        "id": "tl_ev_" + str(gen_id(state, "timeline")),
        "action": "created",
        "timestamp": "2026-03-07T00:00:00Z",
        "userId": state["currentUser"]["id"],
        "details": f"Matter created (duplicated from {orig['displayNumber']})",
    }]
    clone["financials"] = {"workInProgress": 0, "outstandingBalance": 0, "trustFunds": 0, "totalTime": 0, "totalExpenses": 0}
    state["matters"].append(clone)


def solve_task_6(state):
    """Change description of Singh Family Trust."""
    m = find_matter(state, "Singh Family Trust")
    m["description"] = "Singh Family Revocable Living Trust"


def solve_task_7(state):
    """Change responsible attorney on Foster v. Evanston to James Chen."""
    m = find_matter(state, "Foster v. City of Evanston")
    u = find_user_by_name(state, "James Chen")
    m["responsibleAttorneyId"] = u["id"]


def solve_task_8(state):
    """Change originating attorney on Mendez Work Visa to David Kim."""
    m = find_matter(state, "Mendez - Work Visa")
    u = find_user_by_name(state, "David Kim")
    m["originatingAttorneyId"] = u["id"]


def solve_task_9(state):
    """Change responsible staff on Harris v. ABC Construction to Rachel Thompson."""
    m = find_matter(state, "Harris v. ABC Construction")
    u = find_user_by_name(state, "Rachel Thompson")
    m["responsibleStaffId"] = u["id"]


def solve_task_10(state):
    """Change practice area of Singh Family Trust to Tax Law."""
    m = find_matter(state, "Singh Family Trust")
    pa = find_practice_area(state, "Tax Law")
    m["practiceAreaId"] = pa["id"]
    m["matterStageId"] = None  # Tax Law has no stages


def solve_task_11(state):
    """Change location of Mendez Work Visa to Chicago."""
    m = find_matter(state, "Mendez - Work Visa")
    m["location"] = "Chicago"


def solve_task_12(state):
    """Change client ref number of Foster v. Evanston."""
    m = find_matter(state, "Foster v. City of Evanston")
    m["clientRefNumber"] = "SLIP-2024-NEW"


def solve_task_13(state):
    """Change billing method of State v. Morales to flat_rate."""
    m = find_matter(state, "State v. Morales")
    m["billingPreference"]["billingMethod"] = "flat_rate"


def solve_task_14(state):
    """Change stage of Rodriguez v. Premier Auto to Mediation."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    mediation = next(s for s in stages if s["name"] == "Mediation")
    m["matterStageId"] = mediation["id"]


def solve_task_15(state):
    """Change deduction order of Rodriguez v. Premier Auto to expenses_first."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["deductionOrder"] = "expenses_first"


def solve_task_16(state):
    """Add damage 'Prescription medication costs' to Rodriguez v. Premier Auto."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Prescription medication costs",
        "type": "Out-of-Pocket Expenses",
        "category": "Special",
        "amount": 2500,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_17(state):
    """Edit Emergency Room Visit damage amount to 18500."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    d = next(d for d in m["damages"] if d["description"] == "Emergency Room Visit")
    d["amount"] = 18500


def solve_task_18(state):
    """Delete Vehicle repair costs damage."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"] = [d for d in m["damages"] if d["description"] != "Vehicle repair costs"]


def solve_task_19(state):
    """Add recovery from State Farm Insurance for $50000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "State Farm Insurance")
    m["settlement"]["recoveries"].append({
        "id": "rec_" + str(gen_id(state, "recovery")).zfill(3),
        "sourceContactId": c["id"],
        "amount": 50000,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_20(state):
    """Edit Lakeside Insurance recovery to $200000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    rec["amount"] = 200000


def solve_task_21(state):
    """Delete Premier Auto Dealers recovery (cascades to legal fees)."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Premier Auto Dealers")
    # Find the recovery ID to cascade
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    rec_id = rec["id"]
    m["settlement"]["recoveries"] = [r for r in m["settlement"]["recoveries"] if r["sourceContactId"] != c["id"]]
    m["settlement"]["legalFees"] = [lf for lf in m["settlement"]["legalFees"] if lf["recoveryId"] != rec_id]


def solve_task_22(state):
    """Add legal fee for Lakeside recovery, recipient Michael Osei, rate 25."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    u = find_user_by_name(state, "Michael Osei")
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec["id"],
        "recipientId": u["id"],
        "rate": 25,
        "discount": 0,
        "referralFees": [],
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_23(state):
    """Edit legal fee on Lakeside recovery to set discount to 10."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    lf = next(f for f in m["settlement"]["legalFees"] if f["recoveryId"] == rec["id"])
    lf["discount"] = 10


def solve_task_24(state):
    """Delete legal fee for Premier Auto Dealers recovery."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Premier Auto Dealers")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    m["settlement"]["legalFees"] = [f for f in m["settlement"]["legalFees"] if f["recoveryId"] != rec["id"]]


def solve_task_25(state):
    """Add lien from Northwestern Memorial Hospital."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    m["settlement"]["otherLiens"].append({
        "id": "ol_" + str(gen_id(state, "lien")).zfill(3),
        "lienHolderId": c["id"],
        "description": "Hospital treatment lien",
        "amount": 12000,
        "reduction": 0,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_26(state):
    """Edit Riverside Credit Union lien reduction to 1000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    lien = next(l for l in m["settlement"]["otherLiens"] if l["lienHolderId"] == c["id"])
    lien["reduction"] = 1000


def solve_task_27(state):
    """Delete Riverside Credit Union lien."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    m["settlement"]["otherLiens"] = [l for l in m["settlement"]["otherLiens"] if l["lienHolderId"] != c["id"]]


def solve_task_28(state):
    """Add outstanding balance from State Farm Insurance."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "State Farm Insurance")
    m["settlement"]["outstandingBalances"].append({
        "id": "ob_" + str(gen_id(state, "balance")).zfill(3),
        "responsibleParty": "other",
        "balanceHolderId": c["id"],
        "description": "Overpayment recovery",
        "balanceOwing": 1500,
        "reduction": 0,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_29(state):
    """Edit Riverside Credit Union outstanding balance reduction to 500."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    ob = next(b for b in m["settlement"]["outstandingBalances"] if b["balanceHolderId"] == c["id"])
    ob["reduction"] = 500


def solve_task_30(state):
    """Delete Riverside Credit Union outstanding balance."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    m["settlement"]["outstandingBalances"] = [b for b in m["settlement"]["outstandingBalances"] if b["balanceHolderId"] != c["id"]]


def solve_task_31(state):
    """Add medical provider Chicago Physical Therapy Center to Harris v. ABC Construction."""
    m = find_matter(state, "Harris v. ABC Construction")
    c = find_contact_by_name(state, "Chicago Physical Therapy Center")
    m["medicalProviders"].append({
        "id": "mp_" + str(gen_id(state, "medProvider")).zfill(3),
        "contactId": c["id"],
        "description": "Post-surgical hand rehabilitation",
        "treatmentFirstDate": None,
        "treatmentLastDate": None,
        "treatmentComplete": False,
        "recordRequestDate": None,
        "recordFollowUpDate": None,
        "recordStatus": "Not yet requested",
        "billRequestDate": None,
        "billFollowUpDate": None,
        "billStatus": "Not yet requested",
        "medicalRecords": [],
        "medicalBills": [],
    })


def solve_task_32(state):
    """Set treatment last date for Dr. Amanda Reeves on Rodriguez v. Premier Auto."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["treatmentLastDate"] = "2026-01-15"


def solve_task_33(state):
    """Mark treatment complete for Dr. Amanda Reeves."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["treatmentComplete"] = True


def solve_task_34(state):
    """Delete Advanced Imaging Associates provider from Rodriguez v. Premier Auto."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Advanced Imaging Associates")
    m["medicalProviders"] = [p for p in m["medicalProviders"] if p["contactId"] != c["id"]]


def solve_task_35(state):
    """Change record status to Received for Dr. Amanda Reeves."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["recordStatus"] = "Received"


def solve_task_36(state):
    """Add medical record to Northwestern Memorial Hospital provider."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    p["medicalRecords"].append({
        "id": "mr_" + str(gen_id(state, "medRecord")).zfill(3),
        "fileName": "Post_Op_Follow_Up.pdf",
        "receivedDate": "2026-01-10",
        "startDate": "",
        "endDate": "",
        "comments": [],
    })


def solve_task_37(state):
    """Delete medical record Surgical_Report_Lumbar.pdf."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    p["medicalRecords"] = [r for r in p["medicalRecords"] if r["fileName"] != "Surgical_Report_Lumbar.pdf"]


def solve_task_38(state):
    """Add medical bill to Chicago Physical Therapy Center provider."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Chicago Physical Therapy Center")
    p = find_provider(m, c["id"])
    p["medicalBills"].append({
        "id": "mb_" + str(gen_id(state, "medBill")).zfill(3),
        "fileName": "CPTC_Follow_Up_Bill.pdf",
        "billDate": "",
        "receivedDate": "",
        "billAmount": 3500,
        "adjustment": 0,
        "payers": [],
        "balanceOwed": 0,
        "balanceIsLien": False,
        "balanceIsOutstanding": False,
        "comments": [],
    })


def solve_task_39(state):
    """Edit NM_Hospital_Bill.pdf adjustment to 7000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    b = find_bill(p, "NM_Hospital_Bill.pdf")
    b["adjustment"] = 7000


def solve_task_40(state):
    """Delete AIA_Invoice_Aug.pdf from Advanced Imaging Associates."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Advanced Imaging Associates")
    p = find_provider(m, c["id"])
    p["medicalBills"] = [b for b in p["medicalBills"] if b["fileName"] != "AIA_Invoice_Aug.pdf"]


def solve_task_41(state):
    """Add comment to ER_Admission_Report.pdf."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    r = find_record(p, "ER_Admission_Report.pdf")
    r["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Critical evidence for demand package",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-07T00:00:00Z",
    })


def solve_task_42(state):
    """Add comment to CPTC_Bill_Full.pdf."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Chicago Physical Therapy Center")
    p = find_provider(m, c["id"])
    b = find_bill(p, "CPTC_Bill_Full.pdf")
    b["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Insurance reimbursement pending review",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-07T00:00:00Z",
    })


def solve_task_43(state):
    """Delete comment 'Confirms L4-L5 disc herniation' from ER_Admission_Report.pdf."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    r = find_record(p, "ER_Admission_Report.pdf")
    r["comments"] = [cm for cm in r["comments"] if cm["text"] != "Confirms L4-L5 disc herniation"]


def solve_task_44(state):
    """Add practice area 'Civil Litigation'."""
    pa_id = "pa_" + str(gen_id(state, "practiceArea")).zfill(3)
    state["practiceAreas"].append({
        "id": pa_id,
        "name": "Civil Litigation",
        "enabled": True,
        "isPrimary": False,
    })


def solve_task_45(state):
    """Rename 'Insurance Defense' to 'Insurance Law'."""
    pa = find_practice_area(state, "Insurance Defense")
    pa["name"] = "Insurance Law"


def solve_task_46(state):
    """Delete practice area 'Medical Malpractice'."""
    pa = find_practice_area(state, "Medical Malpractice")
    state["practiceAreas"] = [p for p in state["practiceAreas"] if p["id"] != pa["id"]]
    state["matterStages"].pop(pa["id"], None)


def solve_task_47(state):
    """Set 'Criminal Law' as primary practice area."""
    for pa in state["practiceAreas"]:
        pa["isPrimary"] = (pa["name"] == "Criminal Law")


def solve_task_48(state):
    """Add stage 'Case Review' to Personal Injury."""
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
    stages.append({
        "id": stg_id,
        "name": "Case Review",
        "order": len(stages),
    })
    state["matterStages"][pa["id"]] = stages


def solve_task_49(state):
    """Rename 'Initial Consultation' to 'Client Intake' in Personal Injury."""
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    stg = next(s for s in stages if s["name"] == "Initial Consultation")
    stg["name"] = "Client Intake"


def solve_task_50(state):
    """Delete stage 'Sentencing' from Criminal Law."""
    pa = find_practice_area(state, "Criminal Law")
    stages = state["matterStages"].get(pa["id"], [])
    stg = next(s for s in stages if s["name"] == "Sentencing")
    state["matterStages"][pa["id"]] = [s for s in stages if s["id"] != stg["id"]]
    # Unassign any matters using this stage
    for m in state["matters"]:
        if m.get("matterStageId") == stg["id"]:
            m["matterStageId"] = None


def solve_task_51(state):
    """Create template 'Immigration - Work Visa'."""
    pa = find_practice_area(state, "Immigration")
    tmpl_id = "tmpl_" + str(gen_id(state, "template")).zfill(3)
    state["matterTemplates"].append({
        "id": tmpl_id,
        "name": "Immigration - Work Visa",
        "isDefault": False,
        "practiceAreaId": pa["id"],
        "status": "Open",
        "billingMethod": "hourly",
        "description": "",
        "responsibleAttorneyId": None,
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "location": "",
        "isBillable": True,
        "contingencyRate": None,
        "contingencyRecipientId": None,
        "flatFeeAmount": None,
        "flatFeeRecipientId": None,
        "deductionOrder": "fees_first",
        "taskLists": [],
        "documentFolders": [],
        "customFields": [],
        "createdAt": "2026-03-07T00:00:00Z",
        "updatedAt": "2026-03-07T00:00:00Z",
    })


def solve_task_52(state):
    """Edit Criminal Defense template to set responsible staff to Lisa Patel."""
    tmpl = find_template(state, "Criminal Defense - Misdemeanor")
    u = find_user_by_name(state, "Lisa Patel")
    tmpl["responsibleStaffId"] = u["id"]


def solve_task_53(state):
    """Set 'Flat Fee - Simple Will' as default template."""
    for t in state["matterTemplates"]:
        t["isDefault"] = (t["name"] == "Flat Fee - Simple Will")


def solve_task_54(state):
    """Delete template 'Corporate Transaction - M&A'."""
    state["matterTemplates"] = [t for t in state["matterTemplates"] if t["name"] != "Corporate Transaction - M&A"]


def solve_task_55(state):
    """Remove default from 'Personal Injury - Auto Accident' template."""
    tmpl = find_template(state, "Personal Injury - Auto Accident")
    tmpl["isDefault"] = False


def solve_task_56(state):
    """Change numbering starting number to 200."""
    state["numberingScheme"]["nextMatterNumber"] = 200


def solve_task_57(state):
    """Enable auto-update numbering."""
    state["numberingScheme"]["updateByDefault"] = True


SOLVERS = {f"task_{i}": globals()[f"solve_task_{i}"] for i in range(1, 58)}


# -- server management -----------------------------------------------------

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
    """Start the Clio Matters server on the given port."""
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


# -- task runner ------------------------------------------------------------

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
    """Reset -> solve -> verify for a single task."""
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

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


# -- main -------------------------------------------------------------------

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
