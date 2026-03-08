#!/usr/bin/env python3
"""
Sanity check for Clio Matters real tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_real.py                     # All tasks, sequential
    python3 sanity_check_real.py --workers N          # N parallel environments
    python3 sanity_check_real.py --task-id task_e1    # Single task
    python3 sanity_check_real.py --port 9500          # Custom base port
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
TASKS_FILE = APP_DIR / "real-tasks.json"

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
    for e in entities:
        if all(e.get(k) == v for k, v in kwargs.items()):
            return e
    raise ValueError(f"Entity not found: {kwargs}")


def find_matter(state, desc_fragment):
    for m in state["matters"]:
        if desc_fragment in m["description"]:
            return m
    raise ValueError(f"Matter not found containing: {desc_fragment!r}")


def find_contact_by_name(state, name):
    for c in state["contacts"]:
        if c["type"] == "company" and c["lastName"] == name:
            return c
        if c["type"] == "person" and f"{c['firstName']} {c['lastName']}" == name:
            return c
        if c["lastName"] == name:
            return c
    raise ValueError(f"Contact not found: {name!r}")


def find_user_by_name(state, name):
    for u in state["firmUsers"]:
        if u["fullName"] == name:
            return u
    raise ValueError(f"User not found: {name!r}")


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


def find_provider(matter, contact_id):
    for p in matter["medicalProviders"]:
        if p["contactId"] == contact_id:
            return p
    raise ValueError(f"Provider not found with contactId: {contact_id!r}")


def find_record(provider, file_name):
    for r in provider["medicalRecords"]:
        if r["fileName"] == file_name:
            return r
    raise ValueError(f"Record not found: {file_name!r}")


def find_bill(provider, file_name):
    for b in provider["medicalBills"]:
        if b["fileName"] == file_name:
            return b
    raise ValueError(f"Bill not found: {file_name!r}")


def gen_id(state, id_type):
    n = state["_nextIds"][id_type]
    state["_nextIds"][id_type] = n + 1
    return n


# -- solve functions --------------------------------------------------------

# EASY

def solve_task_e1(state):
    """Close the Nguyen divorce case."""
    m = find_matter(state, "Nguyen - Divorce")
    m["status"] = "Closed"
    if not m.get("closedDate"):
        m["closedDate"] = "2026-03-07T00:00:00Z"


def solve_task_e2(state):
    """Reopen the Midwest Manufacturing employment case."""
    m = find_matter(state, "Midwest Manufacturing")
    m["status"] = "Open"
    m["closedDate"] = None


def solve_task_e3(state):
    """Put the Okafor DUI case on hold."""
    m = find_matter(state, "State v. Okafor")
    m["status"] = "Pending"
    if not m.get("pendingDate"):
        m["pendingDate"] = "2026-03-07T00:00:00Z"


def solve_task_e4(state):
    """Delete the Baker residential property purchase matter."""
    idx = next(i for i, m in enumerate(state["matters"])
               if "Baker" in m["description"] and "Residential" in m["description"])
    m = state["matters"].pop(idx)
    state["deletedMatters"].append({
        "id": m["id"], "matterNumber": m["matterNumber"],
        "displayNumber": m["displayNumber"], "description": m["description"],
        "clientId": m["clientId"], "contactName": m["contactName"],
        "deletedAt": "2026-03-07T00:00:00Z", "deletedBy": state["currentUser"]["id"],
        "canRecover": True,
    })


def solve_task_e5(state):
    """Set Corporate Law as the primary practice area."""
    for pa in state["practiceAreas"]:
        pa["isPrimary"] = (pa["name"] == "Corporate Law")


def solve_task_e6(state):
    """Rename Insurance Defense to Insurance Law."""
    pa = find_practice_area(state, "Insurance Defense")
    pa["name"] = "Insurance Law"


def solve_task_e7(state):
    """Add Environmental Law practice area."""
    pa_id = "pa_" + str(gen_id(state, "practiceArea")).zfill(3)
    state["practiceAreas"].append({
        "id": pa_id, "name": "Environmental Law", "enabled": True, "isPrimary": False,
    })


def solve_task_e8(state):
    """Delete Medical Malpractice practice area."""
    pa = find_practice_area(state, "Medical Malpractice")
    state["practiceAreas"] = [p for p in state["practiceAreas"] if p["id"] != pa["id"]]
    state["matterStages"].pop(pa["id"], None)


def solve_task_e9(state):
    """Make Flat Fee - Simple Will template the default."""
    for t in state["matterTemplates"]:
        t["isDefault"] = (t["name"] == "Flat Fee - Simple Will")


def solve_task_e10(state):
    """Delete Corporate Transaction - M&A template."""
    state["matterTemplates"] = [t for t in state["matterTemplates"]
                                if t["name"] != "Corporate Transaction - M&A"]


def solve_task_e11(state):
    """Remove default from PI Auto Accident template."""
    tmpl = find_template(state, "Personal Injury - Auto Accident")
    tmpl["isDefault"] = False


def solve_task_e12(state):
    """Turn on auto-update numbering."""
    state["numberingScheme"]["updateByDefault"] = True


def solve_task_e13(state):
    """Change starting matter number to 200."""
    state["numberingScheme"]["nextMatterNumber"] = 200


def solve_task_e14(state):
    """Switch Rodriguez to expenses-first deduction."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["deductionOrder"] = "expenses_first"


def solve_task_e15(state):
    """Assign James Chen as responsible attorney on Harris case."""
    m = find_matter(state, "Harris v. ABC Construction")
    u = find_user_by_name(state, "James Chen")
    m["responsibleAttorneyId"] = u["id"]


def solve_task_e16(state):
    """Move Cruz bus accident to Investigation stage."""
    m = find_matter(state, "Cruz v. Metro Transit")
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    stg = next(s for s in stages if s["name"] == "Investigation")
    m["matterStageId"] = stg["id"]


def solve_task_e17(state):
    """Switch Morales assault case billing to flat rate."""
    m = find_matter(state, "State v. Morales")
    m["billingPreference"]["billingMethod"] = "flat_rate"


def solve_task_e18(state):
    """Mark treatment complete for Dr. Amanda Reeves on Rodriguez case."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["treatmentComplete"] = True


def solve_task_e19(state):
    """Set Mendez work visa location to Chicago."""
    m = find_matter(state, "Mendez - Work Visa")
    m["location"] = "Chicago"


def solve_task_e20(state):
    """Rename Initial Consultation to Client Intake in Personal Injury."""
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    stg = next(s for s in stages if s["name"] == "Initial Consultation")
    stg["name"] = "Client Intake"


# MEDIUM

def solve_task_m1(state):
    """Add rental car expenses damage to Rodriguez case."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Rental car expenses",
        "type": "Property Damage",
        "category": "Special",
        "amount": 4200,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_m2(state):
    """Add $50,000 recovery from State Farm Insurance to Rodriguez settlement."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "State Farm Insurance")
    m["settlement"]["recoveries"].append({
        "id": "rec_" + str(gen_id(state, "recovery")).zfill(3),
        "sourceContactId": c["id"],
        "amount": 50000,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_m3(state):
    """Add $12,000 lien from Northwestern Memorial Hospital on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    m["settlement"]["otherLiens"].append({
        "id": "ol_" + str(gen_id(state, "lien")).zfill(3),
        "lienHolderId": c["id"],
        "description": "Hospital treatment balance",
        "amount": 12000,
        "reduction": 0,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_m4(state):
    """Add outstanding balance from Riverside CU on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    m["settlement"]["outstandingBalances"].append({
        "id": "ob_" + str(gen_id(state, "balance")).zfill(3),
        "responsibleParty": "other",
        "balanceHolderId": c["id"],
        "description": "Personal loan repayment",
        "balanceOwing": 2500,
        "reduction": 0,
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_m5(state):
    """Create Immigration - Work Visa template."""
    pa = find_practice_area(state, "Immigration")
    tmpl_id = "tmpl_" + str(gen_id(state, "template")).zfill(3)
    state["matterTemplates"].append({
        "id": tmpl_id, "name": "Immigration - Work Visa", "isDefault": False,
        "practiceAreaId": pa["id"], "status": "Open", "billingMethod": "hourly",
        "description": "", "responsibleAttorneyId": None, "originatingAttorneyId": None,
        "responsibleStaffId": None, "location": "", "isBillable": True,
        "contingencyRate": None, "contingencyRecipientId": None,
        "flatFeeAmount": None, "flatFeeRecipientId": None,
        "deductionOrder": "fees_first", "taskLists": [], "documentFolders": [],
        "customFields": [],
        "createdAt": "2026-03-07T00:00:00Z", "updatedAt": "2026-03-07T00:00:00Z",
    })


def solve_task_m6(state):
    """Add medical record Post_Op_Evaluation.pdf to NM Hospital on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    p["medicalRecords"].append({
        "id": "mr_" + str(gen_id(state, "medRecord")).zfill(3),
        "fileName": "Post_Op_Evaluation.pdf",
        "receivedDate": "2026-01-10",
        "startDate": "",
        "endDate": "",
        "comments": [],
    })


def solve_task_m7(state):
    """Add medical bill CPTC_Additional_Bill.pdf to Chicago PT on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Chicago Physical Therapy Center")
    p = find_provider(m, c["id"])
    p["medicalBills"].append({
        "id": "mb_" + str(gen_id(state, "medBill")).zfill(3),
        "fileName": "CPTC_Additional_Bill.pdf",
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


def solve_task_m8(state):
    """Update Rodriguez: client ref and location."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["clientRefNumber"] = "REF-2026-UPDATED"
    m["location"] = "Northern District of Illinois"


def solve_task_m9(state):
    """Increase Emergency Room Visit damage to $18,500."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    d = next(d for d in m["damages"] if d["description"] == "Emergency Room Visit")
    d["amount"] = 18500


def solve_task_m10(state):
    """Update Lakeside Insurance recovery to $200,000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    rec["amount"] = 200000


def solve_task_m11(state):
    """Set legal fee discount to 15% on Lakeside recovery."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    lf = next(f for f in m["settlement"]["legalFees"] if f["recoveryId"] == rec["id"])
    lf["discount"] = 15


def solve_task_m12(state):
    """Change NM_Hospital_Bill adjustment to $7,000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p = find_provider(m, c["id"])
    b = find_bill(p, "NM_Hospital_Bill.pdf")
    b["adjustment"] = 7000


def solve_task_m13(state):
    """Switch Singh billing to hourly, currency to CAD."""
    m = find_matter(state, "Singh Family Trust")
    m["billingPreference"]["billingMethod"] = "hourly"
    m["billingPreference"]["currency"] = "CAD"


def solve_task_m14(state):
    """Duplicate Cruz v. Metro Transit matter."""
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
    clone["financials"] = {"workInProgress": 0, "outstandingBalance": 0,
                           "trustFunds": 0, "totalTime": 0, "totalExpenses": 0}
    state["matters"].append(clone)


def solve_task_m15(state):
    """Foster case: responsible attorney David Kim, staff Lisa Patel."""
    m = find_matter(state, "Foster v. City of Evanston")
    m["responsibleAttorneyId"] = find_user_by_name(state, "David Kim")["id"]
    m["responsibleStaffId"] = find_user_by_name(state, "Lisa Patel")["id"]


def solve_task_m16(state):
    """Add Expert Review stage to Criminal Law."""
    pa = find_practice_area(state, "Criminal Law")
    stages = state["matterStages"].get(pa["id"], [])
    stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
    stages.append({"id": stg_id, "name": "Expert Review", "order": len(stages)})
    state["matterStages"][pa["id"]] = stages


def solve_task_m17(state):
    """Update Criminal Defense template: responsible staff Lisa Patel."""
    tmpl = find_template(state, "Criminal Defense - Misdemeanor")
    u = find_user_by_name(state, "Lisa Patel")
    tmpl["responsibleStaffId"] = u["id"]


def solve_task_m18(state):
    """Set $1,000 reduction on Riverside CU lien in Rodriguez settlement."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    lien = next(l for l in m["settlement"]["otherLiens"] if l["lienHolderId"] == c["id"])
    lien["reduction"] = 1000


def solve_task_m19(state):
    """Change Kowalski to Personal Injury practice area."""
    m = find_matter(state, "Kowalski")
    pa = find_practice_area(state, "Personal Injury")
    m["practiceAreaId"] = pa["id"]
    # Assign first PI stage
    stages = state["matterStages"].get(pa["id"], [])
    if stages:
        m["matterStageId"] = stages[0]["id"]


def solve_task_m20(state):
    """Remove Advanced Imaging Associates from Rodriguez case."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Advanced Imaging Associates")
    m["medicalProviders"] = [p for p in m["medicalProviders"] if p["contactId"] != c["id"]]


# HARD

def solve_task_h1(state):
    """Close all open Personal Injury cases."""
    pa = find_practice_area(state, "Personal Injury")
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            m["status"] = "Closed"
            if not m.get("closedDate"):
                m["closedDate"] = "2026-03-07T00:00:00Z"


def solve_task_h2(state):
    """Put both Criminal Law cases on hold."""
    pa = find_practice_area(state, "Criminal Law")
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            m["status"] = "Pending"
            if not m.get("pendingDate"):
                m["pendingDate"] = "2026-03-07T00:00:00Z"


def solve_task_h3(state):
    """Rodriguez: Mediation stage, expenses first, Lakeside recovery $225,000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    mediation = next(s for s in stages if s["name"] == "Mediation")
    m["matterStageId"] = mediation["id"]
    m["deductionOrder"] = "expenses_first"
    c = find_contact_by_name(state, "Lakeside Insurance Co.")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == c["id"])
    rec["amount"] = 225000


def solve_task_h4(state):
    """Reassign all of Michael Osei's cases to Maria Garcia."""
    osei = find_user_by_name(state, "Michael Osei")
    garcia = find_user_by_name(state, "Maria Garcia")
    for m in state["matters"]:
        if m["responsibleAttorneyId"] == osei["id"]:
            m["responsibleAttorneyId"] = garcia["id"]


def solve_task_h5(state):
    """Remove Premier Auto recovery, increase Lakeside to $250,000."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    premier = find_contact_by_name(state, "Premier Auto Dealers")
    lakeside = find_contact_by_name(state, "Lakeside Insurance Co.")
    # Find and remove Premier Auto recovery and its legal fees
    premier_rec = next(r for r in m["settlement"]["recoveries"]
                       if r["sourceContactId"] == premier["id"])
    m["settlement"]["recoveries"] = [r for r in m["settlement"]["recoveries"]
                                     if r["sourceContactId"] != premier["id"]]
    m["settlement"]["legalFees"] = [lf for lf in m["settlement"]["legalFees"]
                                    if lf["recoveryId"] != premier_rec["id"]]
    # Update Lakeside recovery
    lakeside_rec = next(r for r in m["settlement"]["recoveries"]
                        if r["sourceContactId"] == lakeside["id"])
    lakeside_rec["amount"] = 250000


def solve_task_h6(state):
    """Add two damages to Harris case."""
    m = find_matter(state, "Harris v. ABC Construction")
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Physical therapy - 12 sessions",
        "type": "Medical Expenses",
        "category": "Special",
        "amount": 6000,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Emotional distress from workplace trauma",
        "type": "Emotional Distress",
        "category": "General",
        "amount": 25000,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h7(state):
    """Delete all damages from Foster case."""
    m = find_matter(state, "Foster v. City of Evanston")
    m["damages"] = []


def solve_task_h8(state):
    """Add State Farm recovery and legal fee on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "State Farm Insurance")
    garcia = find_user_by_name(state, "Maria Garcia")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    m["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": c["id"],
        "amount": 50000,
        "createdAt": "2026-03-07T00:00:00Z",
    })
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": garcia["id"],
        "rate": 33.33,
        "discount": 0,
        "referralFees": [],
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_h9(state):
    """Add Dr. Reeves provider on Cruz case, treatment complete, records Requested."""
    m = find_matter(state, "Cruz v. Metro Transit")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    m["medicalProviders"].append({
        "id": "mp_" + str(gen_id(state, "medProvider")).zfill(3),
        "contactId": c["id"],
        "description": "Orthopedic evaluation",
        "treatmentFirstDate": None,
        "treatmentLastDate": None,
        "treatmentComplete": True,
        "recordRequestDate": None,
        "recordFollowUpDate": None,
        "recordStatus": "Requested",
        "billRequestDate": None,
        "billFollowUpDate": None,
        "billStatus": "Not yet requested",
        "medicalRecords": [],
        "medicalBills": [],
    })


def solve_task_h10(state):
    """Delete Riverside CU lien and outstanding balance from Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Riverside Community Credit Union")
    m["settlement"]["otherLiens"] = [l for l in m["settlement"]["otherLiens"]
                                     if l["lienHolderId"] != c["id"]]
    m["settlement"]["outstandingBalances"] = [b for b in m["settlement"]["outstandingBalances"]
                                              if b["balanceHolderId"] != c["id"]]


def solve_task_h11(state):
    """Rename Flat Fee template, billing hourly, staff Lisa Patel."""
    tmpl = find_template(state, "Flat Fee - Simple Will")
    tmpl["name"] = "Estate Planning - Comprehensive"
    tmpl["billingMethod"] = "hourly"
    tmpl["responsibleStaffId"] = find_user_by_name(state, "Lisa Patel")["id"]


def solve_task_h12(state):
    """Add Emergency Orders and Property Division to Family Law."""
    pa = find_practice_area(state, "Family Law")
    stages = state["matterStages"].get(pa["id"], [])
    for name in ["Emergency Orders", "Property Division"]:
        stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
        stages.append({"id": stg_id, "name": name, "order": len(stages)})
    state["matterStages"][pa["id"]] = stages


def solve_task_h13(state):
    """Baker: attorney Jennifer Walsh, Closing stage, ref RE-2026-FINAL."""
    m = find_matter(state, "Baker - Residential")
    m["responsibleAttorneyId"] = find_user_by_name(state, "Jennifer Walsh")["id"]
    pa_id = m["practiceAreaId"]
    stages = state["matterStages"].get(pa_id, [])
    closing = next(s for s in stages if s["name"] == "Closing")
    m["matterStageId"] = closing["id"]
    m["clientRefNumber"] = "RE-2026-FINAL"


def solve_task_h14(state):
    """Add comments to ER_Admission_Report.pdf and CPTC_Bill_Full.pdf on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    # Comment on ER_Admission_Report.pdf (NM Hospital)
    nm = find_contact_by_name(state, "Northwestern Memorial Hospital")
    p1 = find_provider(m, nm["id"])
    r = find_record(p1, "ER_Admission_Report.pdf")
    r["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Critical documentation for settlement negotiations",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-07T00:00:00Z",
    })
    # Comment on CPTC_Bill_Full.pdf (Chicago PT)
    cpt = find_contact_by_name(state, "Chicago Physical Therapy Center")
    p2 = find_provider(m, cpt["id"])
    b = find_bill(p2, "CPTC_Bill_Full.pdf")
    b["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Insurance payment verified",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-07T00:00:00Z",
    })


def solve_task_h15(state):
    """Delete Vehicle repair costs, add Rental vehicle damage on Rodriguez."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"] = [d for d in m["damages"] if d["description"] != "Vehicle repair costs"]
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Rental vehicle and transportation",
        "type": "Out-of-Pocket Expenses",
        "category": "Special",
        "amount": 5500,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h16(state):
    """Rename Criminal Defense template, attorney Michael Osei, staff Lisa Patel."""
    tmpl = find_template(state, "Criminal Defense - Misdemeanor")
    tmpl["name"] = "Criminal Defense - General"
    tmpl["responsibleAttorneyId"] = find_user_by_name(state, "Michael Osei")["id"]
    tmpl["responsibleStaffId"] = find_user_by_name(state, "Lisa Patel")["id"]


def solve_task_h17(state):
    """Kowalski to Personal Injury, Initial Consultation stage."""
    m = find_matter(state, "Kowalski")
    pa = find_practice_area(state, "Personal Injury")
    m["practiceAreaId"] = pa["id"]
    stages = state["matterStages"].get(pa["id"], [])
    init = next(s for s in stages if s["name"] == "Initial Consultation")
    m["matterStageId"] = init["id"]


def solve_task_h18(state):
    """Rodriguez: Dr. Reeves bill request Requested on 2026-03-01, record status Received."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["billStatus"] = "Requested"
    p["billRequestDate"] = "2026-03-01"
    p["recordStatus"] = "Received"


def solve_task_h19(state):
    """Close Nguyen, reopen Midwest Manufacturing, delete Baker."""
    # Close Nguyen
    m1 = find_matter(state, "Nguyen - Divorce")
    m1["status"] = "Closed"
    if not m1.get("closedDate"):
        m1["closedDate"] = "2026-03-07T00:00:00Z"
    # Reopen Midwest Manufacturing
    m2 = find_matter(state, "Midwest Manufacturing")
    m2["status"] = "Open"
    m2["closedDate"] = None
    # Delete Baker
    idx = next(i for i, m in enumerate(state["matters"])
               if "Baker" in m["description"] and "Residential" in m["description"])
    m3 = state["matters"].pop(idx)
    state["deletedMatters"].append({
        "id": m3["id"], "matterNumber": m3["matterNumber"],
        "displayNumber": m3["displayNumber"], "description": m3["description"],
        "clientId": m3["clientId"], "contactName": m3["contactName"],
        "deletedAt": "2026-03-07T00:00:00Z", "deletedBy": state["currentUser"]["id"],
        "canRecover": True,
    })


def solve_task_h20(state):
    """Create new matter for Angela Rodriguez, PI, Maria Garcia, contingency 33.33%."""
    contact = find_contact_by_name(state, "Angela Rodriguez")
    garcia = find_user_by_name(state, "Maria Garcia")
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    first_stage = stages[0]["id"] if stages else None
    num = str(gen_id(state, "matter")).zfill(5)
    matter = {
        "id": "mat_" + num,
        "matterNumber": num,
        "displayNumber": num + "-Rodriguez",
        "description": "Rodriguez - Property Damage Claim",
        "clientId": contact["id"],
        "contactName": "Angela Rodriguez",
        "status": "Open",
        "practiceAreaId": pa["id"],
        "matterStageId": first_stage,
        "responsibleAttorneyId": garcia["id"],
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientRefNumber": "",
        "location": "",
        "openDate": "2026-03-07T00:00:00Z",
        "pendingDate": None,
        "closedDate": None,
        "createdAt": "2026-03-07T00:00:00Z",
        "updatedAt": "2026-03-07T00:00:00Z",
        "permissions": {"type": "everyone"},
        "blockedUsers": [],
        "billingPreference": {
            "isBillable": True,
            "billingMethod": "contingency",
            "currency": "USD",
            "contingencyRate": 33.33,
            "contingencyRecipientId": garcia["id"],
            "flatFeeAmount": None,
            "flatFeeRecipientId": None,
            "customRates": [],
            "budget": None,
            "budgetNotifyUsers": [],
            "trustMinBalance": None,
            "trustNotifyUsers": [],
        },
        "deductionOrder": "fees_first",
        "relatedContacts": [],
        "notifications": [],
        "customFields": [],
        "taskLists": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingAllocation": 0, "responsibleAllocation": 0},
        "templateId": None,
        "financials": {"workInProgress": 0, "outstandingBalance": 0, "trustFunds": 0, "totalTime": 0, "totalExpenses": 0},
        "timeline": [{
            "id": "tl_ev_" + str(gen_id(state, "timeline")),
            "action": "created",
            "timestamp": "2026-03-07T00:00:00Z",
            "userId": state["currentUser"]["id"],
            "details": "Matter created",
        }],
        "damages": [],
        "medicalProviders": [],
        "settlement": {"recoveries": [], "legalFees": [], "otherLiens": [], "outstandingBalances": [], "expenses": []},
    }
    state["matters"].append(matter)


# HARDENING ROUND 1

def solve_task_h21(state):
    """Add $100,000 Punitive Damages to the open PI case with the largest total damages."""
    pa = find_practice_area(state, "Personal Injury")
    best_matter = None
    best_total = -1
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            total = sum(d["amount"] for d in m.get("damages", []))
            if total > best_total:
                best_total = total
                best_matter = m
    best_matter["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Punitive Damages",
        "type": "Punitive Damages",
        "category": "Other",
        "amount": 100000,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h22(state):
    """Rodriguez: responsible = TechNova's responsible, originating = TechNova's originating."""
    technova = find_matter(state, "TechNova Solutions")
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    rodriguez["responsibleAttorneyId"] = technova["responsibleAttorneyId"]
    rodriguez["originatingAttorneyId"] = technova["originatingAttorneyId"]


def solve_task_h23(state):
    """Close all Chen's open matters, put all Osei's open matters on hold."""
    chen = find_user_by_name(state, "James Chen")
    osei = find_user_by_name(state, "Michael Osei")
    for m in state["matters"]:
        if m["responsibleAttorneyId"] == chen["id"] and m["status"] == "Open":
            m["status"] = "Closed"
            if not m.get("closedDate"):
                m["closedDate"] = "2026-03-07T00:00:00Z"
        elif m["responsibleAttorneyId"] == osei["id"] and m["status"] == "Open":
            m["status"] = "Pending"
            if not m.get("pendingDate"):
                m["pendingDate"] = "2026-03-07T00:00:00Z"


def solve_task_h24(state):
    """Rodriguez: find provider with billStatus Incomplete, set Received, add bill."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    provider = None
    for p in m["medicalProviders"]:
        if p.get("billStatus") == "Incomplete":
            provider = p
            break
    provider["billStatus"] = "Received"
    provider["medicalBills"].append({
        "id": "mb_" + str(gen_id(state, "medBill")).zfill(3),
        "fileName": "Final_Invoice.pdf",
        "billDate": "",
        "receivedDate": "",
        "billAmount": 2800,
        "adjustment": 0,
        "payers": [],
        "balanceOwed": 0,
        "balanceIsLien": False,
        "balanceIsOutstanding": False,
        "comments": [],
    })


def solve_task_h25(state):
    """Rodriguez: set recordStatus Complete for diagnostic imaging provider (con_020)."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Advanced Imaging Associates")
    p = find_provider(m, c["id"])
    p["recordStatus"] = "Complete"


def solve_task_h26(state):
    """Rodriguez: add 5% referral fee on Premier Auto legal fee to Carlos Espinoza."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    premier = find_contact_by_name(state, "Premier Auto Dealers")
    espinoza = find_contact_by_name(state, "Carlos Espinoza")
    rec = next(r for r in m["settlement"]["recoveries"] if r["sourceContactId"] == premier["id"])
    lf = next(f for f in m["settlement"]["legalFees"] if f["recoveryId"] == rec["id"])
    lf["referralFees"].append({"recipientId": espinoza["id"], "rate": 5})


def solve_task_h27(state):
    """Disable Workers Comp, move Kowalski to PI Demand Letter, hourly billing."""
    wc = find_practice_area(state, "Workers Compensation")
    wc["enabled"] = False
    pi = find_practice_area(state, "Personal Injury")
    m = find_matter(state, "Kowalski")
    m["practiceAreaId"] = pi["id"]
    stages = state["matterStages"].get(pi["id"], [])
    demand = next(s for s in stages if s["name"] == "Demand Letter")
    m["matterStageId"] = demand["id"]
    m["billingPreference"]["billingMethod"] = "hourly"


def solve_task_h28(state):
    """Rodriguez: delete all General damages, add consolidated $250k Pain and Suffering."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"] = [d for d in m["damages"] if d.get("category") != "General"]
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Consolidated general damages",
        "type": "Pain and Suffering",
        "category": "General",
        "amount": 250000,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h29(state):
    """Assign paralegal with most open matters as responsible staff on Singh case."""
    paralegals = [u for u in state["firmUsers"] if u["role"] == "Paralegal"]
    counts = {}
    for u in paralegals:
        counts[u["id"]] = sum(
            1 for m in state["matters"]
            if m.get("responsibleStaffId") == u["id"] and m["status"] == "Open"
        )
    best_id = max(counts, key=counts.get)
    m = find_matter(state, "Singh Family Trust")
    m["responsibleStaffId"] = best_id


def solve_task_h30(state):
    """Foster: add $100k State Farm recovery + legal fee (Osei, 40%, 10% discount)."""
    m = find_matter(state, "Foster v. City of Evanston")
    sf = find_contact_by_name(state, "State Farm Insurance")
    osei = find_user_by_name(state, "Michael Osei")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    m["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": sf["id"],
        "amount": 100000,
        "createdAt": "2026-03-07T00:00:00Z",
    })
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": osei["id"],
        "rate": 40,
        "discount": 10,
        "referralFees": [],
        "createdAt": "2026-03-07T00:00:00Z",
    })


def solve_task_h31(state):
    """Rodriguez: Dr. Reeves — set last treatment date 2026-02-28, mark complete."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    c = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, c["id"])
    p["treatmentLastDate"] = "2026-02-28"
    p["treatmentComplete"] = True


def solve_task_h32(state):
    """Create Civil Litigation PA, add Pre-Trial and Trial stages, create template."""
    pa_id = "pa_" + str(gen_id(state, "practiceArea")).zfill(3)
    state["practiceAreas"].append({
        "id": pa_id, "name": "Civil Litigation", "enabled": True, "isPrimary": False,
    })
    stages = []
    for i, name in enumerate(["Pre-Trial", "Trial"]):
        stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
        stages.append({"id": stg_id, "name": name, "order": i})
    state["matterStages"][pa_id] = stages
    tmpl_id = "tmpl_" + str(gen_id(state, "template")).zfill(3)
    state["matterTemplates"].append({
        "id": tmpl_id, "name": "Civil Litigation - Standard", "isDefault": False,
        "practiceAreaId": pa_id, "status": "Open", "billingMethod": "hourly",
        "description": "", "responsibleAttorneyId": None, "originatingAttorneyId": None,
        "responsibleStaffId": None, "location": "", "isBillable": True,
        "contingencyRate": None, "contingencyRecipientId": None,
        "flatFeeAmount": None, "flatFeeRecipientId": None,
        "deductionOrder": "fees_first", "taskLists": [], "documentFolders": [],
        "customFields": [],
        "createdAt": "2026-03-07T00:00:00Z", "updatedAt": "2026-03-07T00:00:00Z",
    })


def solve_task_h33(state):
    """Rodriguez: remove payers from bills that have them, recalc balance owed."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        for b in p["medicalBills"]:
            if b.get("payers"):
                b["payers"] = []
                b["balanceOwed"] = b["billAmount"] - b.get("adjustment", 0)


def solve_task_h34(state):
    """Rodriguez: add comment to every bill that has payers."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        for b in p["medicalBills"]:
            if b.get("payers"):
                b["comments"].append({
                    "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
                    "text": "Bill verified and approved",
                    "userId": state["currentUser"]["id"],
                    "timestamp": "2026-03-07T00:00:00Z",
                })


def solve_task_h35(state):
    """Nguyen (DuPage+Pending): location → Cook County, staff → Rodriguez's staff."""
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    nguyen = find_matter(state, "Nguyen - Divorce")
    nguyen["location"] = "Cook County Circuit Court"
    nguyen["responsibleStaffId"] = rodriguez["responsibleStaffId"]


def solve_task_h36(state):
    """Cruz: add AIA provider, record status Requested, add Cervical_MRI_Cruz.pdf."""
    m = find_matter(state, "Cruz v. Metro Transit")
    aia = find_contact_by_name(state, "Advanced Imaging Associates")
    mp_id = "mp_" + str(gen_id(state, "medProvider")).zfill(3)
    mr_id = "mr_" + str(gen_id(state, "medRecord")).zfill(3)
    m["medicalProviders"].append({
        "id": mp_id,
        "contactId": aia["id"],
        "description": "MRI cervical spine evaluation",
        "treatmentFirstDate": None,
        "treatmentLastDate": None,
        "treatmentComplete": False,
        "recordRequestDate": "2026-03-01",
        "recordFollowUpDate": None,
        "recordStatus": "Requested",
        "billRequestDate": None,
        "billFollowUpDate": None,
        "billStatus": "Not yet requested",
        "medicalRecords": [{
            "id": mr_id,
            "fileName": "Cervical_MRI_Cruz.pdf",
            "receivedDate": "2026-03-15",
            "startDate": "",
            "endDate": "",
            "comments": [],
        }],
        "medicalBills": [],
    })


def solve_task_h37(state):
    """Harris: contingency 40%, add Disfigurement $10k, move to Demand Letter."""
    m = find_matter(state, "Harris v. ABC Construction")
    m["billingPreference"]["contingencyRate"] = 40
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Disfigurement",
        "type": "Disfigurement",
        "category": "General",
        "amount": 10000,
        "createdAt": "2026-03-07T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    demand = next(s for s in stages if s["name"] == "Demand Letter")
    m["matterStageId"] = demand["id"]


def solve_task_h38(state):
    """Rodriguez: comment on first record of provider with highest total bill amount."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    best_provider = None
    best_total = -1
    for p in m["medicalProviders"]:
        total = sum(b["billAmount"] for b in p.get("medicalBills", []))
        if total > best_total:
            best_total = total
            best_provider = p
    first_record = best_provider["medicalRecords"][0]
    first_record["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Flagged for settlement review",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-07T00:00:00Z",
    })


def solve_task_h39(state):
    """Rename PI Auto Accident template, hourly, not default, David Kim as attorney."""
    tmpl = find_template(state, "Personal Injury - Auto Accident")
    tmpl["name"] = "Personal Injury - General"
    tmpl["billingMethod"] = "hourly"
    tmpl["isDefault"] = False
    tmpl["responsibleAttorneyId"] = find_user_by_name(state, "David Kim")["id"]


def solve_task_h40(state):
    """Rodriguez: CPTC balance as lien, AIA not outstanding, NM adjustment $10k."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        for b in p["medicalBills"]:
            if b["fileName"] == "CPTC_Bill_Full.pdf":
                b["balanceIsLien"] = True
            elif b["fileName"] == "AIA_Invoice_Aug.pdf":
                b["balanceIsOutstanding"] = False
            elif b["fileName"] == "NM_Hospital_Bill.pdf":
                b["adjustment"] = 10000


# HARDENING ROUND 2

def solve_task_h41(state):
    """Rodriguez: responsible = highest-paid partner, originating = highest-paid associate."""
    partners = [u for u in state["firmUsers"] if u["role"] == "Partner"]
    associates = [u for u in state["firmUsers"] if u["role"] == "Associate"]
    best_partner = max(partners, key=lambda u: u["rate"])
    best_associate = max(associates, key=lambda u: u["rate"])
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["responsibleAttorneyId"] = best_partner["id"]
    m["originatingAttorneyId"] = best_associate["id"]


def solve_task_h42(state):
    """Foster: add $75k Lakeside recovery + legal fee matching Rodriguez's Lakeside fee."""
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    foster = find_matter(state, "Foster v. City of Evanston")
    lakeside = find_contact_by_name(state, "Lakeside Insurance Co.")
    rod_rec = next(r for r in rodriguez["settlement"]["recoveries"]
                   if r["sourceContactId"] == lakeside["id"])
    rod_lf = next(f for f in rodriguez["settlement"]["legalFees"]
                  if f["recoveryId"] == rod_rec["id"])
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    foster["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": lakeside["id"],
        "amount": 75000,
        "createdAt": "2026-03-08T00:00:00Z",
    })
    foster["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": rod_lf["recipientId"],
        "rate": rod_lf["rate"],
        "discount": rod_lf["discount"],
        "referralFees": [],
        "createdAt": "2026-03-08T00:00:00Z",
    })


def solve_task_h43(state):
    """Rodriguez: add comment to rehabilitation provider's bill."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    cpt = find_contact_by_name(state, "Chicago Physical Therapy Center")
    p = find_provider(m, cpt["id"])
    b = p["medicalBills"][0]
    b["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Pending insurance adjuster review",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-08T00:00:00Z",
    })


def solve_task_h44(state):
    """Rodriguez: swap lien and outstanding flags on every medical bill."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        for b in p["medicalBills"]:
            old_lien = b.get("balanceIsLien", False)
            old_outstanding = b.get("balanceIsOutstanding", False)
            b["balanceIsLien"] = old_outstanding
            b["balanceIsOutstanding"] = old_lien


def solve_task_h45(state):
    """Mendez: less expensive partner as responsible, more expensive as originating."""
    partners = [u for u in state["firmUsers"] if u["role"] == "Partner"]
    partners_sorted = sorted(partners, key=lambda u: u["rate"])
    m = find_matter(state, "Mendez - Work Visa")
    m["responsibleAttorneyId"] = partners_sorted[0]["id"]
    m["originatingAttorneyId"] = partners_sorted[-1]["id"]


def solve_task_h46(state):
    """Cruz: copy budget, trust min, trust notify users from Rodriguez."""
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    cruz = find_matter(state, "Cruz v. Metro Transit")
    rod_bp = rodriguez["billingPreference"]
    cruz_bp = cruz["billingPreference"]
    cruz_bp["budget"] = rod_bp["budget"]
    cruz_bp["trustMinBalance"] = rod_bp["trustMinBalance"]
    cruz_bp["trustNotifyUsers"] = list(rod_bp["trustNotifyUsers"])


def solve_task_h47(state):
    """Increase contingency rate by 5 on every open contingency matter."""
    for m in state["matters"]:
        bp = m["billingPreference"]
        if m["status"] == "Open" and bp["billingMethod"] == "contingency":
            bp["contingencyRate"] = round(bp["contingencyRate"] + 5, 2)


def solve_task_h48(state):
    """Cruz: $45k NM Hospital recovery + legal fee (Garcia 33.33%, 5% discount) + CPTC lien."""
    m = find_matter(state, "Cruz v. Metro Transit")
    nm = find_contact_by_name(state, "Northwestern Memorial Hospital")
    garcia = find_user_by_name(state, "Maria Garcia")
    cptc = find_contact_by_name(state, "Chicago Physical Therapy Center")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    m["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": nm["id"],
        "amount": 45000,
        "createdAt": "2026-03-08T00:00:00Z",
    })
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": garcia["id"],
        "rate": 33.33,
        "discount": 5,
        "referralFees": [],
        "createdAt": "2026-03-08T00:00:00Z",
    })
    m["settlement"]["otherLiens"].append({
        "id": "ol_" + str(gen_id(state, "lien")).zfill(3),
        "lienHolderId": cptc["id"],
        "description": "Outstanding treatment balance",
        "amount": 3500,
        "reduction": 0,
        "createdAt": "2026-03-08T00:00:00Z",
    })


def solve_task_h49(state):
    """Criminal Defense template: attorney with most open matters, contingency 30%."""
    counts = {}
    for m in state["matters"]:
        if m["status"] == "Open":
            atty = m.get("responsibleAttorneyId")
            if atty:
                counts[atty] = counts.get(atty, 0) + 1
    best_atty_id = max(counts, key=counts.get)
    tmpl = find_template(state, "Criminal Defense - Misdemeanor")
    tmpl["responsibleAttorneyId"] = best_atty_id
    tmpl["billingMethod"] = "contingency"
    tmpl["contingencyRate"] = 30


def solve_task_h50(state):
    """Advance open PI cases past Investigation to next stage."""
    pa = find_practice_area(state, "Personal Injury")
    stages = sorted(state["matterStages"][pa["id"]], key=lambda s: s["order"])
    stage_index = {s["id"]: i for i, s in enumerate(stages)}
    investigation_idx = next(i for i, s in enumerate(stages) if s["name"] == "Investigation")
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            cur_idx = stage_index.get(m["matterStageId"])
            if cur_idx is not None and cur_idx > investigation_idx and cur_idx + 1 < len(stages):
                m["matterStageId"] = stages[cur_idx + 1]["id"]


def solve_task_h51(state):
    """Close open matter with highest trust, assign its attorney to Singh."""
    best_matter = None
    best_trust = -1
    for m in state["matters"]:
        if m["status"] == "Open":
            trust = m.get("financials", {}).get("trustFunds", 0)
            if trust > best_trust:
                best_trust = trust
                best_matter = m
    best_matter["status"] = "Closed"
    best_matter["closedDate"] = "2026-03-08T00:00:00Z"
    singh = find_matter(state, "Singh Family Trust")
    singh["responsibleAttorneyId"] = best_matter["responsibleAttorneyId"]


def solve_task_h52(state):
    """Add 2 damages to the open PI case with smallest total damages."""
    pa = find_practice_area(state, "Personal Injury")
    best_matter = None
    best_total = float("inf")
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            total = sum(d["amount"] for d in m.get("damages", []))
            if total < best_total:
                best_total = total
                best_matter = m
    best_matter["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Future medical care",
        "type": "Future Medical Costs",
        "category": "Special",
        "amount": 20000,
        "createdAt": "2026-03-08T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })
    best_matter["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Lost earning capacity",
        "type": "Loss of Earning Capacity",
        "category": "Special",
        "amount": 15000,
        "createdAt": "2026-03-08T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h53(state):
    """Rodriguez: delete Special damages under $20k, Orthopedic Surgery to $90k."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["damages"] = [
        d for d in m["damages"]
        if not (d["category"] == "Special" and d["amount"] < 20000)
    ]
    ortho = next(d for d in m["damages"] if d["description"] == "Orthopedic Surgery")
    ortho["amount"] = 90000


def solve_task_h54(state):
    """Rodriguez: update bill of provider with earliest treatment start date."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    best_provider = None
    earliest = None
    for p in m["medicalProviders"]:
        d = p.get("treatmentFirstDate")
        if d and (earliest is None or d < earliest):
            earliest = d
            best_provider = p
    bill = best_provider["medicalBills"][0]
    bill["billAmount"] = 50000
    bill["adjustment"] = 8000


def solve_task_h55(state):
    """Rodriguez: comment on bill with highest balance owed."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    best_bill = None
    best_balance = -1
    for p in m["medicalProviders"]:
        for b in p["medicalBills"]:
            if b.get("balanceOwed", 0) > best_balance:
                best_balance = b["balanceOwed"]
                best_bill = b
    best_bill["comments"].append({
        "id": "cmt_" + str(gen_id(state, "comment")).zfill(3),
        "text": "Priority collection \u2014 escalate to senior partner",
        "userId": state["currentUser"]["id"],
        "timestamp": "2026-03-08T00:00:00Z",
    })


def solve_task_h56(state):
    """Morales on hold, transfer staff to Harris, Harris to Demand Letter."""
    morales = find_matter(state, "State v. Morales")
    harris = find_matter(state, "Harris v. ABC Construction")
    morales["status"] = "Pending"
    if not morales.get("pendingDate"):
        morales["pendingDate"] = "2026-03-08T00:00:00Z"
    harris["responsibleStaffId"] = morales["responsibleStaffId"]
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"][pa["id"]]
    demand = next(s for s in stages if s["name"] == "Demand Letter")
    harris["matterStageId"] = demand["id"]


def solve_task_h57(state):
    """Harris: add Dr. Reeves provider with record and bill."""
    m = find_matter(state, "Harris v. ABC Construction")
    reeves = find_contact_by_name(state, "Dr. Amanda Reeves")
    mp_id = "mp_" + str(gen_id(state, "medProvider")).zfill(3)
    mr_id = "mr_" + str(gen_id(state, "medRecord")).zfill(3)
    mb_id = "mb_" + str(gen_id(state, "medBill")).zfill(3)
    m["medicalProviders"].append({
        "id": mp_id,
        "contactId": reeves["id"],
        "description": "Hand specialist evaluation",
        "treatmentFirstDate": "2026-02-01",
        "treatmentLastDate": None,
        "treatmentComplete": True,
        "recordRequestDate": None,
        "recordFollowUpDate": None,
        "recordStatus": "Not yet requested",
        "billRequestDate": None,
        "billFollowUpDate": None,
        "billStatus": "Not yet requested",
        "medicalRecords": [{
            "id": mr_id,
            "fileName": "Hand_Specialist_Report.pdf",
            "receivedDate": "2026-03-05",
            "startDate": "",
            "endDate": "",
            "comments": [],
        }],
        "medicalBills": [{
            "id": mb_id,
            "fileName": "Reeves_Consult_Bill.pdf",
            "billDate": "",
            "receivedDate": "",
            "billAmount": 4500,
            "adjustment": 500,
            "payers": [],
            "balanceOwed": 0,
            "balanceIsLien": False,
            "balanceIsOutstanding": False,
            "comments": [],
        }],
    })


def solve_task_h58(state):
    """Close every open matter with zero trust funds and zero WIP."""
    for m in state["matters"]:
        if m["status"] == "Open":
            fin = m.get("financials", {})
            if fin.get("trustFunds", 0) == 0 and fin.get("workInProgress", 0) == 0:
                m["status"] = "Closed"
                if not m.get("closedDate"):
                    m["closedDate"] = "2026-03-08T00:00:00Z"


def solve_task_h59(state):
    """Rodriguez: Premier Auto legal fee discount to 10%, add Espinoza referral 7.5%."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    premier = find_contact_by_name(state, "Premier Auto Dealers")
    espinoza = find_contact_by_name(state, "Carlos Espinoza")
    rec = next(r for r in m["settlement"]["recoveries"]
               if r["sourceContactId"] == premier["id"])
    lf = next(f for f in m["settlement"]["legalFees"]
              if f["recoveryId"] == rec["id"])
    lf["discount"] = 10
    lf["referralFees"].append({"recipientId": espinoza["id"], "rate": 7.5})


def solve_task_h60(state):
    """Nguyen: reopen, staff=Thompson, contingency 35% (Garcia), Trial/Hearing."""
    m = find_matter(state, "Nguyen - Divorce")
    thompson = find_user_by_name(state, "Rachel Thompson")
    garcia = find_user_by_name(state, "Maria Garcia")
    m["status"] = "Open"
    m["pendingDate"] = None
    m["responsibleStaffId"] = thompson["id"]
    bp = m["billingPreference"]
    bp["billingMethod"] = "contingency"
    bp["contingencyRate"] = 35
    bp["contingencyRecipientId"] = garcia["id"]
    fl = find_practice_area(state, "Family Law")
    stages = state["matterStages"][fl["id"]]
    trial = next(s for s in stages if s["name"] == "Trial/Hearing")
    m["matterStageId"] = trial["id"]


# HARDENING ROUND 3

def solve_task_h61(state):
    """Swap billing: contingency→hourly, hourly→flat_rate for all open matters."""
    originals = {}
    for m in state["matters"]:
        if m["status"] == "Open":
            originals[m["id"]] = m["billingPreference"]["billingMethod"]
    for m in state["matters"]:
        if m["status"] == "Open":
            orig = originals[m["id"]]
            if orig == "contingency":
                m["billingPreference"]["billingMethod"] = "hourly"
            elif orig == "hourly":
                m["billingPreference"]["billingMethod"] = "flat_rate"


def solve_task_h62(state):
    """Cruz: $60k recovery from Rodriguez NM Hospital bill payer, legal fee with highest-rate member at 30%."""
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    nm = find_contact_by_name(state, "Northwestern Memorial Hospital")
    nm_provider = find_provider(rodriguez, nm["id"])
    payer_id = nm_provider["medicalBills"][0]["payers"][0]["payerId"]
    highest = max(state["firmUsers"], key=lambda u: u["rate"])
    cruz = find_matter(state, "Cruz v. Metro Transit")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    cruz["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": payer_id,
        "amount": 60000,
        "createdAt": "2026-03-08T00:00:00Z",
    })
    cruz["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": highest["id"],
        "rate": 30,
        "discount": 0,
        "referralFees": [],
        "createdAt": "2026-03-08T00:00:00Z",
    })


def solve_task_h63(state):
    """Create new matter for Okafor client under Criminal Law with Osei, hourly."""
    okafor = find_matter(state, "State v. Okafor")
    client_id = okafor["clientId"]
    contact_name = okafor["contactName"]
    osei = find_user_by_name(state, "Michael Osei")
    criminal = find_practice_area(state, "Criminal Law")
    stages = state["matterStages"].get(criminal["id"], [])
    first_stage = stages[0]["id"] if stages else None
    num = str(gen_id(state, "matter")).zfill(5)
    matter = {
        "id": "mat_" + num,
        "matterNumber": num,
        "displayNumber": num + "-" + contact_name.split()[-1],
        "description": "Okafor - Civil Rights Claim",
        "clientId": client_id,
        "contactName": contact_name,
        "status": "Open",
        "practiceAreaId": criminal["id"],
        "matterStageId": first_stage,
        "responsibleAttorneyId": osei["id"],
        "originatingAttorneyId": None,
        "responsibleStaffId": None,
        "clientRefNumber": "",
        "location": "",
        "openDate": "2026-03-08T00:00:00Z",
        "pendingDate": None,
        "closedDate": None,
        "createdAt": "2026-03-08T00:00:00Z",
        "updatedAt": "2026-03-08T00:00:00Z",
        "permissions": {"type": "everyone"},
        "blockedUsers": [],
        "billingPreference": {
            "isBillable": True,
            "billingMethod": "hourly",
            "currency": "USD",
            "contingencyRate": None,
            "contingencyRecipientId": None,
            "flatFeeAmount": None,
            "flatFeeRecipientId": None,
            "customRates": [],
            "budget": None,
            "budgetNotifyUsers": [],
            "trustMinBalance": None,
            "trustNotifyUsers": [],
        },
        "deductionOrder": "fees_first",
        "relatedContacts": [],
        "notifications": [],
        "customFields": [],
        "taskLists": [],
        "documentFolders": [],
        "reports": {"useFirmSettings": True, "originatingAllocation": 0, "responsibleAllocation": 0},
        "templateId": None,
        "financials": {"workInProgress": 0, "outstandingBalance": 0, "trustFunds": 0, "totalTime": 0, "totalExpenses": 0},
        "timeline": [{
            "id": "tl_ev_" + str(gen_id(state, "timeline")),
            "action": "created",
            "timestamp": "2026-03-08T00:00:00Z",
            "userId": state["currentUser"]["id"],
            "details": "Matter created",
        }],
        "damages": [],
        "medicalProviders": [],
        "settlement": {"recoveries": [], "legalFees": [], "otherLiens": [], "outstandingBalances": [], "expenses": []},
    }
    state["matters"].append(matter)


def solve_task_h64(state):
    """Rodriguez: set billStatus to Requested for providers with 'Not yet requested'."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        if p.get("billStatus") == "Not yet requested":
            p["billStatus"] = "Requested"
            p["billRequestDate"] = "2026-03-05"


def solve_task_h65(state):
    """Add Arbitration stage to PI, move Rodriguez to it."""
    pa = find_practice_area(state, "Personal Injury")
    stages = state["matterStages"].get(pa["id"], [])
    stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
    stages.append({"id": stg_id, "name": "Arbitration", "order": len(stages)})
    state["matterStages"][pa["id"]] = stages
    m = find_matter(state, "Rodriguez v. Premier Auto")
    m["matterStageId"] = stg_id


def solve_task_h66(state):
    """Open matter with highest WIP: staff=Thompson, originating=Garcia."""
    best = max(
        (m for m in state["matters"] if m["status"] == "Open"),
        key=lambda m: m.get("financials", {}).get("workInProgress", 0),
    )
    thompson = find_user_by_name(state, "Rachel Thompson")
    garcia = find_user_by_name(state, "Maria Garcia")
    best["responsibleStaffId"] = thompson["id"]
    best["originatingAttorneyId"] = garcia["id"]


def solve_task_h67(state):
    """Rodriguez: double recoveries, increase legal fee rates by 5."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for r in m["settlement"]["recoveries"]:
        r["amount"] = r["amount"] * 2
    for f in m["settlement"]["legalFees"]:
        f["rate"] = round(f["rate"] + 5, 2)


def solve_task_h68(state):
    """Harris: $75k Lakeside recovery, legal fee at 35% with Harris resp atty, 5% referral to Espinoza."""
    m = find_matter(state, "Harris v. ABC Construction")
    lakeside = find_contact_by_name(state, "Lakeside Insurance Co.")
    espinoza = find_contact_by_name(state, "Carlos Espinoza")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    m["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": lakeside["id"],
        "amount": 75000,
        "createdAt": "2026-03-08T00:00:00Z",
    })
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": m["responsibleAttorneyId"],
        "rate": 35,
        "discount": 0,
        "referralFees": [{"recipientId": espinoza["id"], "rate": 5}],
        "createdAt": "2026-03-08T00:00:00Z",
    })


def solve_task_h69(state):
    """Create Maritime Law PA, 4 stages, move Kowalski to Investigation."""
    pa_id = "pa_" + str(gen_id(state, "practiceArea")).zfill(3)
    state["practiceAreas"].append({
        "id": pa_id, "name": "Maritime Law", "enabled": True, "isPrimary": False,
    })
    stages = []
    for i, name in enumerate(["Case Intake", "Investigation", "Arbitration", "Settlement"]):
        stg_id = "stg_" + str(gen_id(state, "stage")).zfill(3)
        stages.append({"id": stg_id, "name": name, "order": i})
    state["matterStages"][pa_id] = stages
    investigation = stages[1]
    m = find_matter(state, "Kowalski")
    m["practiceAreaId"] = pa_id
    m["matterStageId"] = investigation["id"]


def solve_task_h70(state):
    """Add lien matching outstanding balance holder and amount on matter with balances."""
    for m in state["matters"]:
        if m["status"] != "Open":
            continue
        balances = m.get("settlement", {}).get("outstandingBalances", [])
        if balances:
            balance = balances[0]
            m["settlement"]["otherLiens"].append({
                "id": "ol_" + str(gen_id(state, "lien")).zfill(3),
                "lienHolderId": balance["balanceHolderId"],
                "description": "Additional services rendered",
                "amount": balance["balanceOwing"],
                "reduction": 0,
                "createdAt": "2026-03-08T00:00:00Z",
            })
            break


def solve_task_h71(state):
    """Rodriguez: set recordFollowUpDate for providers with recordStatus='Received'."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    for p in m["medicalProviders"]:
        if p.get("recordStatus") == "Received":
            p["recordFollowUpDate"] = "2026-03-15"


def solve_task_h72(state):
    """Singh: resp attorney from TechNova, originating from Rodriguez."""
    technova = find_matter(state, "TechNova Solutions")
    rodriguez = find_matter(state, "Rodriguez v. Premier Auto")
    singh = find_matter(state, "Singh Family Trust")
    singh["responsibleAttorneyId"] = technova["responsibleAttorneyId"]
    singh["originatingAttorneyId"] = rodriguez["originatingAttorneyId"]


def solve_task_h73(state):
    """Delete all closed matters."""
    closed = [m for m in state["matters"] if m["status"] == "Closed"]
    for m in closed:
        state["deletedMatters"].append({
            "id": m["id"], "matterNumber": m["matterNumber"],
            "displayNumber": m["displayNumber"], "description": m["description"],
            "clientId": m["clientId"], "contactName": m["contactName"],
            "deletedAt": "2026-03-08T00:00:00Z", "deletedBy": state["currentUser"]["id"],
            "canRecover": True,
        })
    state["matters"] = [m for m in state["matters"] if m["status"] != "Closed"]


def solve_task_h74(state):
    """Rodriguez: add damage with amount = sum of settlement expenses."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    total = sum(e["amount"] for e in m["settlement"]["expenses"])
    m["damages"].append({
        "id": "dmg_" + str(gen_id(state, "damage")).zfill(3),
        "description": "Out-of-pocket travel expenses",
        "type": "Out-of-Pocket Expenses",
        "category": "Special",
        "amount": total,
        "createdAt": "2026-03-08T00:00:00Z",
        "createdBy": state["currentUser"]["id"],
    })


def solve_task_h75(state):
    """Rodriguez: add Reeves_Evaluation.pdf bill to Dr. Reeves."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    reeves = find_contact_by_name(state, "Dr. Amanda Reeves")
    p = find_provider(m, reeves["id"])
    p["medicalBills"].append({
        "id": "mb_" + str(gen_id(state, "medBill")).zfill(3),
        "fileName": "Reeves_Evaluation.pdf",
        "billDate": "",
        "receivedDate": "",
        "billAmount": 5000,
        "adjustment": 500,
        "payers": [],
        "balanceOwed": 4500,
        "balanceIsLien": False,
        "balanceIsOutstanding": True,
        "comments": [],
    })


def solve_task_h76(state):
    """Move all open PI matters to first stage."""
    pa = find_practice_area(state, "Personal Injury")
    stages = sorted(state["matterStages"][pa["id"]], key=lambda s: s["order"])
    first_stage = stages[0]
    for m in state["matters"]:
        if m["practiceAreaId"] == pa["id"] and m["status"] == "Open":
            m["matterStageId"] = first_stage["id"]


def solve_task_h77(state):
    """Rodriguez: remove Riverside CU lien, create outstanding balance with same amount."""
    m = find_matter(state, "Rodriguez v. Premier Auto")
    riverside = find_contact_by_name(state, "Riverside Community Credit Union")
    lien = next(l for l in m["settlement"]["otherLiens"] if l["lienHolderId"] == riverside["id"])
    lien_amount = lien["amount"]
    m["settlement"]["otherLiens"] = [l for l in m["settlement"]["otherLiens"]
                                     if l["lienHolderId"] != riverside["id"]]
    m["settlement"]["outstandingBalances"].append({
        "id": "ob_" + str(gen_id(state, "balance")).zfill(3),
        "responsibleParty": "client",
        "balanceHolderId": riverside["id"],
        "description": "Converted from lien",
        "balanceOwing": lien_amount,
        "reduction": 0,
        "createdAt": "2026-03-08T00:00:00Z",
    })


def solve_task_h78(state):
    """Change all hourly templates to contingency at 25%."""
    for t in state["matterTemplates"]:
        if t["billingMethod"] == "hourly":
            t["billingMethod"] = "contingency"
            t["contingencyRate"] = 25


def solve_task_h79(state):
    """Open matter with 2nd highest trust: billing=flat_rate, staff=Thompson."""
    open_matters = [m for m in state["matters"] if m["status"] == "Open"]
    sorted_by_trust = sorted(
        open_matters,
        key=lambda m: m.get("financials", {}).get("trustFunds", 0),
        reverse=True,
    )
    target = sorted_by_trust[1]
    thompson = find_user_by_name(state, "Rachel Thompson")
    target["billingPreference"]["billingMethod"] = "flat_rate"
    target["responsibleStaffId"] = thompson["id"]


def solve_task_h80(state):
    """Okafor: State Farm recovery, Chen legal fee at 25%, Riverside CU lien $3k."""
    m = find_matter(state, "State v. Okafor")
    sf = find_contact_by_name(state, "State Farm Insurance")
    chen = find_user_by_name(state, "James Chen")
    riverside = find_contact_by_name(state, "Riverside Community Credit Union")
    rec_id = "rec_" + str(gen_id(state, "recovery")).zfill(3)
    m["settlement"]["recoveries"].append({
        "id": rec_id,
        "sourceContactId": sf["id"],
        "amount": 35000,
        "createdAt": "2026-03-08T00:00:00Z",
    })
    m["settlement"]["legalFees"].append({
        "id": "lf_" + str(gen_id(state, "legalFee")).zfill(3),
        "recoveryId": rec_id,
        "recipientId": chen["id"],
        "rate": 25,
        "discount": 0,
        "referralFees": [],
        "createdAt": "2026-03-08T00:00:00Z",
    })
    m["settlement"]["otherLiens"].append({
        "id": "ol_" + str(gen_id(state, "lien")).zfill(3),
        "lienHolderId": riverside["id"],
        "description": "Outstanding personal loan",
        "amount": 3000,
        "reduction": 0,
        "createdAt": "2026-03-08T00:00:00Z",
    })


SOLVERS = {}
for _name, _fn in list(globals().items()):
    if _name.startswith("solve_task_"):
        _task_id = _name.replace("solve_", "")
        SOLVERS[_task_id] = _fn


# -- server management -----------------------------------------------------

def generate_seed_state():
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True, text=True,
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


def find_free_port(start=9000):
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
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
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


# -- task runner ------------------------------------------------------------

def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        time.sleep(0.3)

        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
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
            result = run_single_task(task, server_url)
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
    parser = argparse.ArgumentParser(description="Clio Matters real-task sanity check")
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
