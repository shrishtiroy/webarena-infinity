#!/usr/bin/env python3
"""
Sanity check for real-tasks verifiers in the Elation Prescriptions app.

For each task, directly constructs the expected end-state (bypassing the UI),
writes it to the server, then runs the verifier and asserts it passes.
"""

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "real-tasks.json"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def get_seed_state():
    """Load seed data by evaluating data.js via Node."""
    data_js = APP_DIR / "js" / "data.js"
    node_script = r"""
    const fs = require('fs');
    const code = fs.readFileSync('%s', 'utf8');
    const fn = new Function(code + `; return {
        SEED_DATA_VERSION, CURRENT_USER, CURRENT_PATIENT,
        PERMANENT_RX_MEDS, PERMANENT_OTC_MEDS, TEMPORARY_MEDS,
        DISCONTINUED_MEDS, CANCELED_SCRIPTS, PHARMACIES,
        REFILL_REQUESTS, CHANGE_REQUESTS, RX_TEMPLATES,
        CUSTOM_SIGS, MEDICATION_DATABASE, DRUG_INTERACTIONS,
        FORMULARY_DATA, SETTINGS, PROVIDERS, DIAGNOSIS_CODES
    }`);
    const data = fn();
    const state = {
        _seedVersion: data.SEED_DATA_VERSION,
        currentUser: data.CURRENT_USER,
        currentPatient: data.CURRENT_PATIENT,
        permanentRxMeds: data.PERMANENT_RX_MEDS,
        permanentOtcMeds: data.PERMANENT_OTC_MEDS,
        temporaryMeds: data.TEMPORARY_MEDS,
        discontinuedMeds: data.DISCONTINUED_MEDS,
        canceledScripts: data.CANCELED_SCRIPTS,
        pharmacies: data.PHARMACIES,
        refillRequests: data.REFILL_REQUESTS,
        changeRequests: data.CHANGE_REQUESTS,
        rxTemplates: data.RX_TEMPLATES,
        customSigs: data.CUSTOM_SIGS,
        medicationDatabase: data.MEDICATION_DATABASE,
        drugInteractions: data.DRUG_INTERACTIONS,
        formularyData: data.FORMULARY_DATA,
        settings: data.SETTINGS,
        providers: data.PROVIDERS,
        diagnosisCodes: data.DIAGNOSIS_CODES,
        _nextPrxId: 100,
        _nextOtcId: 100,
        _nextTmpId: 100,
        _nextDiscId: 100,
        _nextCxlId: 100,
        _nextRrId: 100,
        _nextCrId: 100,
        _nextTplId: 100,
        _nextSigId: 100,
        _nextAlgId: 100
    };
    console.log(JSON.stringify(state));
    """ % str(data_js).replace("\\", "\\\\")

    result = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(f"Node.js error: {result.stderr}")
    return json.loads(result.stdout)


def find_entity(lst, **kwargs):
    """Find first entity matching all key=value pairs."""
    for item in lst:
        if all(item.get(k) == v for k, v in kwargs.items()):
            return item
    return None


def find_entity_containing(lst, field, substring):
    """Find first entity where field contains substring (case-insensitive)."""
    for item in lst:
        if substring.lower() in item.get(field, "").lower():
            return item
    return None


def remove_entity(lst, **kwargs):
    """Remove and return first entity matching criteria."""
    for i, item in enumerate(lst):
        if all(item.get(k) == v for k, v in kwargs.items()):
            return lst.pop(i)
    raise ValueError(f"Entity not found: {kwargs}")


def load_verifier(verify_path):
    full_path = str(APP_DIR / verify_path)
    spec = importlib.util.spec_from_file_location("verifier", full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


NOW_DATE = "2026-03-02"
NOW_ISO = "2026-03-02T12:00:00.000Z"
CURRENT_USER_NAME = "Dr. Sarah Mitchell"
CURRENT_USER_ID = "prov_001"


# ──────────────────────────────────────────────
# Shared mutation helpers
# ──────────────────────────────────────────────

def _approve_refill(state, med_name, modifications=None):
    """Approve a refill request and update linked medication."""
    req = find_entity(state["refillRequests"], medicationName=med_name, status="pending")
    req["status"] = "approved"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME
    if modifications:
        req["modifications"] = modifications
    if req.get("patientMedId"):
        med = find_entity(state["permanentRxMeds"], medicationName=med_name)
        if med:
            med["lastPrescribedDate"] = NOW_DATE
            if modifications and modifications.get("refills") is not None:
                med["refillsRemaining"] = modifications["refills"]
            if modifications and modifications.get("sig"):
                med["sig"] = modifications["sig"]


def _deny_refill(state, med_name, reason):
    """Deny a refill request with a reason."""
    req = find_entity(state["refillRequests"], medicationName=med_name, status="pending")
    req["status"] = "denied"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME
    req["denyReason"] = reason


def _discontinue_med(state, med_name, source_list_key, reason, details="", send_cancel=False):
    """Discontinue a medication, optionally creating a cancel script."""
    med = remove_entity(state[source_list_key], medicationName=med_name)
    med["status"] = "discontinued"
    med["classification"] = "discontinued"
    med["discontinuedDate"] = NOW_DATE
    med["discontinuedBy"] = CURRENT_USER_NAME
    med["discontinueReason"] = reason
    med["discontinueDetails"] = details
    if send_cancel and med.get("pharmacyId"):
        cxl_id = f"cxl_{state['_nextCxlId']:03d}"
        state["canceledScripts"].append({
            "id": cxl_id,
            "medicationName": med["medicationName"],
            "ndc": med.get("ndc"),
            "sig": med["sig"],
            "qty": med["qty"],
            "refills": med.get("refills", 0),
            "daysSupply": med.get("daysSupply", 30),
            "status": "canceled",
            "classification": "canceled",
            "prescriberId": med.get("prescriberId"),
            "prescriberName": med.get("prescriberName"),
            "pharmacyId": med["pharmacyId"],
            "pharmacyName": med.get("pharmacyName"),
            "prescribedDate": med.get("lastPrescribedDate"),
            "canceledDate": NOW_DATE,
            "cancelReason": "Medication discontinued: " + reason,
            "diagnosis": med.get("diagnosis", [])
        })
        state["_nextCxlId"] += 1
    state["discontinuedMeds"].append(med)


def _add_prescription(state, med_name, sig, qty, unit, refills, days_supply,
                      classification, pharmacy_name=None, diagnosis=None,
                      daw=False, instructions="", is_controlled=False,
                      schedule_class=None):
    """Add a new prescription to state."""
    pharmacy_id = None
    pharm_name = None
    if pharmacy_name:
        pharm = find_entity_containing(state["pharmacies"], "name", pharmacy_name)
        if pharm:
            pharmacy_id = pharm["id"]
            pharm_name = pharm["name"]

    prx_id = f"prx_{state['_nextPrxId']:03d}"
    med = {
        "id": prx_id,
        "medicationName": med_name,
        "ndc": None,
        "sig": sig,
        "qty": qty,
        "unit": unit,
        "refills": refills,
        "refillsRemaining": refills,
        "daysSupply": days_supply,
        "dispenseAsWritten": daw,
        "status": "active",
        "classification": classification,
        "prescriberId": CURRENT_USER_ID,
        "prescriberName": CURRENT_USER_NAME,
        "pharmacyId": pharmacy_id,
        "pharmacyName": pharm_name,
        "startDate": NOW_DATE,
        "lastPrescribedDate": NOW_DATE,
        "lastFilledDate": None,
        "nextRefillDate": None,
        "diagnosis": diagnosis or [],
        "isControlled": is_controlled,
        "scheduleClass": schedule_class,
        "instructionsToPharmacy": instructions,
        "doNotFillBefore": None
    }
    if classification == "temporary":
        state["temporaryMeds"].append(med)
    elif classification == "permanent_otc":
        state["permanentOtcMeds"].append(med)
    else:
        state["permanentRxMeds"].append(med)
    state["_nextPrxId"] += 1
    return med


def _document_med(state, med_name, sig, med_type="otc", qty=0, unit="tablets",
                  days_supply=30, diagnosis=None):
    """Document an existing medication the patient is taking."""
    if med_type == "otc":
        med_id = f"otc_{state['_nextOtcId']:03d}"
        state["_nextOtcId"] += 1
        classification = "permanent_otc"
    else:
        med_id = f"prx_{state['_nextPrxId']:03d}"
        state["_nextPrxId"] += 1
        classification = "permanent_rx"

    med = {
        "id": med_id,
        "medicationName": med_name,
        "ndc": None,
        "sig": sig,
        "qty": qty,
        "unit": unit,
        "refills": 0,
        "refillsRemaining": 0,
        "daysSupply": days_supply,
        "dispenseAsWritten": False,
        "status": "active",
        "classification": classification,
        "prescriberId": None,
        "prescriberName": None,
        "pharmacyId": None,
        "pharmacyName": None,
        "startDate": NOW_DATE,
        "lastPrescribedDate": None,
        "documentedDate": NOW_DATE,
        "diagnosis": diagnosis or [],
        "isControlled": False,
        "scheduleClass": None
    }
    if med_type == "otc":
        state["permanentOtcMeds"].append(med)
    else:
        state["permanentRxMeds"].append(med)
    return med


# ──────────────────────────────────────────────
# Solve functions — one per task
# ──────────────────────────────────────────────

# === EASY ===

def solve_task_e1(state):
    """Approve Lisinopril refill."""
    _approve_refill(state, "Lisinopril 10mg tablet")


def solve_task_e2(state):
    """Approve Omeprazole refill."""
    _approve_refill(state, "Omeprazole 20mg capsule")


def solve_task_e3(state):
    """Approve Sertraline refill."""
    _approve_refill(state, "Sertraline 50mg tablet")


def solve_task_e4(state):
    """Deny Atorvastatin refill."""
    _deny_refill(state, "Atorvastatin 20mg tablet", "Patient needs lipid panel before renewal")


def solve_task_e5(state):
    """Remove Latex allergy."""
    allergies = state["currentPatient"]["allergies"]
    remove_entity(allergies, allergen="Latex")


def solve_task_e6(state):
    """Remove Codeine allergy."""
    allergies = state["currentPatient"]["allergies"]
    remove_entity(allergies, allergen="Codeine")


def solve_task_e7(state):
    """Remove Prednisone taper template."""
    remove_entity(state["rxTemplates"], medicationName="Prednisone 10mg tablet (taper)")


def solve_task_e8(state):
    """Remove Azithromycin Z-Pack template."""
    remove_entity(state["rxTemplates"], medicationName="Azithromycin 250mg tablet (Z-Pack)")


def solve_task_e9(state):
    """Disable drug-to-allergy alerts."""
    state["settings"]["drugDecisionSupport"]["drugToAllergyEnabled"] = False


def solve_task_e10(state):
    """Set drug-to-drug level to major_only."""
    state["settings"]["drugDecisionSupport"]["drugToDrugLevel"] = "major_only"


def solve_task_e11(state):
    """Disable auto-populate last pharmacy."""
    state["settings"]["autoPopulateLastPharmacy"] = False


def solve_task_e12(state):
    """Disable cost estimates."""
    state["settings"]["showCostEstimates"] = False


def solve_task_e13(state):
    """Disable formulary data."""
    state["settings"]["showFormularyData"] = False


def solve_task_e14(state):
    """Delete injectable sig shortcut."""
    remove_entity(state["customSigs"], text="Inject subcutaneously once weekly")


def solve_task_e15(state):
    """Delete ophthalmic sig shortcut."""
    remove_entity(state["customSigs"], text="Instill 1 drop in affected eye(s) twice daily")


def solve_task_e16(state):
    """Move Amoxicillin from temporary to permanent Rx."""
    med = remove_entity(state["temporaryMeds"], medicationName="Amoxicillin 500mg capsule")
    med["classification"] = "permanent_rx"
    state["permanentRxMeds"].append(med)


def solve_task_e17(state):
    """Move Montelukast from permanent Rx to temporary."""
    med = remove_entity(state["permanentRxMeds"], medicationName="Montelukast 10mg tablet")
    med["classification"] = "temporary"
    state["temporaryMeds"].append(med)


def solve_task_e18(state):
    """Move Prednisone from temporary to permanent Rx."""
    med = remove_entity(state["temporaryMeds"], medicationName="Prednisone 10mg tablet")
    med["classification"] = "permanent_rx"
    state["permanentRxMeds"].append(med)


def solve_task_e19(state):
    """Approve Atorvastatin to Rosuvastatin change request."""
    req = find_entity(state["changeRequests"], originalMedication="Atorvastatin 20mg tablet")
    req["status"] = "approved"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME


def solve_task_e20(state):
    """Deny Gabapentin sig clarification change request."""
    req = find_entity(state["changeRequests"], medicationName="Gabapentin 300mg capsule")
    req["status"] = "denied"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME
    req["denyReason"] = "Current sig is correct as written"


# === MEDIUM ===

def solve_task_m1(state):
    """Approve Gabapentin refill with modified sig to twice daily."""
    _approve_refill(state, "Gabapentin 300mg capsule",
                    modifications={"sig": "Take 1 capsule by mouth twice daily"})


def solve_task_m2(state):
    """Approve Metoprolol refill with 3 refills."""
    _approve_refill(state, "Metoprolol Succinate ER 50mg tablet",
                    modifications={"refills": 3})


def solve_task_m3(state):
    """Deny Sertraline refill — needs follow-up."""
    _deny_refill(state, "Sertraline 50mg tablet", "Requires follow-up appointment")


def solve_task_m4(state):
    """Approve Metoprolol refill with morning dosing."""
    _approve_refill(state, "Metoprolol Succinate ER 50mg tablet",
                    modifications={"sig": "Take 1 tablet by mouth once daily in the morning"})


def solve_task_m5(state):
    """Discontinue Omeprazole."""
    _discontinue_med(state, "Omeprazole 20mg capsule", "permanentRxMeds",
                     "I want to discontinue this medication", "Switching to famotidine")


def solve_task_m6(state):
    """Discontinue Amlodipine with cancel request."""
    _discontinue_med(state, "Amlodipine 5mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", send_cancel=True)


def solve_task_m7(state):
    """Discontinue Montelukast — patient stopped."""
    _discontinue_med(state, "Montelukast 10mg tablet", "permanentRxMeds",
                     "Patient stopped taking medication")


def solve_task_m8(state):
    """Discontinue Ciprofloxacin."""
    _discontinue_med(state, "Ciprofloxacin 500mg tablet", "temporaryMeds",
                     "I want to discontinue this medication")


def solve_task_m9(state):
    """Prescribe Levothyroxine 50mcg to CVS."""
    _add_prescription(state, "Levothyroxine 50mcg tablet",
                      "Take 1 tablet by mouth once daily on empty stomach",
                      30, "tablets", 5, 30, "permanent_rx", "CVS Pharmacy #4521")


def solve_task_m10(state):
    """Prescribe Cyclobenzaprine 10mg as temporary."""
    _add_prescription(state, "Cyclobenzaprine 10mg tablet",
                      "Take 1 tablet by mouth three times daily as needed for muscle spasm",
                      30, "tablets", 0, 10, "temporary")


def solve_task_m11(state):
    """Prescribe Famotidine 20mg with DAW to CVS."""
    _add_prescription(state, "Famotidine 20mg tablet",
                      "Take 1 tablet by mouth twice daily",
                      60, "tablets", 3, 30, "permanent_rx", "CVS Pharmacy #4521",
                      daw=True)


def solve_task_m12(state):
    """Add Ibuprofen drug allergy."""
    state["currentPatient"]["allergies"].append({
        "id": f"alg_{state['_nextAlgId']:03d}",
        "allergen": "Ibuprofen",
        "reaction": "Stomach upset, GI bleeding",
        "severity": "Moderate",
        "type": "drug",
        "onsetDate": NOW_DATE,
        "source": "provider-entered"
    })
    state["_nextAlgId"] += 1


def solve_task_m13(state):
    """Add Levothyroxine template."""
    tpl_id = f"tpl_{state['_nextTplId']:03d}"
    state["rxTemplates"].append({
        "id": tpl_id,
        "medicationName": "Levothyroxine 50mcg tablet",
        "sig": "Take 1 tablet by mouth once daily on empty stomach",
        "qty": 30,
        "unit": "tablets",
        "refills": 5,
        "daysSupply": 30,
        "ndc": None,
        "createdDate": NOW_DATE
    })
    state["_nextTplId"] += 1


def solve_task_m14(state):
    """Update Metformin template qty to 90."""
    tpl = find_entity(state["rxTemplates"], medicationName="Metformin 500mg tablet")
    tpl["qty"] = 90


def solve_task_m15(state):
    """Change default pharmacy to Walgreens #7892."""
    pharm = find_entity_containing(state["pharmacies"], "name", "Walgreens #7892")
    state["settings"]["defaultPharmacyId"] = pharm["id"]


def solve_task_m16(state):
    """Add oral custom sig."""
    sig_id = f"sig_{state['_nextSigId']:03d}"
    state["customSigs"].append({
        "id": sig_id,
        "text": "Take 2 capsules by mouth once daily with breakfast",
        "category": "oral"
    })
    state["_nextSigId"] += 1


def solve_task_m17(state):
    """Add topical patch sig."""
    sig_id = f"sig_{state['_nextSigId']:03d}"
    state["customSigs"].append({
        "id": sig_id,
        "text": "Apply 1 patch to skin every 72 hours",
        "category": "topical"
    })
    state["_nextSigId"] += 1


def solve_task_m18(state):
    """Update sublingual sig text."""
    sig = find_entity(state["customSigs"], text="Dissolve 1 tablet under the tongue as needed")
    sig["text"] = "Dissolve 1 tablet under the tongue every 5 minutes as needed, max 3 doses"


def solve_task_m19(state):
    """Document Glucosamine as OTC."""
    _document_med(state, "Glucosamine 1500mg tablet",
                  "Take 1 tablet by mouth once daily")


def solve_task_m20(state):
    """Complete reconciliation without changes."""
    state["currentPatient"]["lastReconciledDate"] = NOW_ISO


# === HARD ===

def solve_task_h1(state):
    """Process 3 refills: approve Lisinopril + Omeprazole, deny Atorvastatin."""
    _approve_refill(state, "Lisinopril 10mg tablet")
    _approve_refill(state, "Omeprazole 20mg capsule")
    _deny_refill(state, "Atorvastatin 20mg tablet", "Patient needs lipid panel before renewal")


def solve_task_h2(state):
    """Discontinue Sertraline with cancel request."""
    _discontinue_med(state, "Sertraline 50mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", send_cancel=True)


def solve_task_h3(state):
    """Reconcile and discontinue Aspirin 81mg."""
    state["currentPatient"]["lastReconciledDate"] = NOW_ISO
    _discontinue_med(state, "Aspirin 81mg tablet (low-dose)", "permanentOtcMeds",
                     "I want to discontinue this medication")


def solve_task_h4(state):
    """Bulk refill Lisinopril and Metformin."""
    lisinopril = find_entity(state["permanentRxMeds"], medicationName="Lisinopril 10mg tablet")
    metformin = find_entity(state["permanentRxMeds"], medicationName="Metformin 500mg tablet")
    for orig in [lisinopril, metformin]:
        _add_prescription(state, orig["medicationName"], orig["sig"],
                          orig["qty"], orig["unit"], orig["refills"],
                          orig["daysSupply"], "permanent_rx",
                          orig.get("pharmacyName"))


def solve_task_h5(state):
    """Prescribe Albuterol inhaler for asthma to CVS."""
    _add_prescription(state, "Albuterol 90mcg/actuation inhaler",
                      "Inhale 1-2 puffs every 4-6 hours as needed",
                      1, "inhalers", 2, 30, "permanent_rx", "CVS Pharmacy #4521",
                      diagnosis=[{"code": "J45.20", "description": "Mild intermittent asthma"}])


def solve_task_h6(state):
    """Prescribe 14-day Doxycycline 100mg as temporary to Walgreens."""
    _add_prescription(state, "Doxycycline 100mg capsule",
                      "Take 1 capsule by mouth twice daily for 14 days",
                      28, "capsules", 0, 14, "temporary", "Walgreens #7892")


def solve_task_h7(state):
    """Prescribe Ondansetron 4mg as temporary with pharmacy instructions."""
    _add_prescription(state, "Ondansetron 4mg tablet",
                      "Take 1 tablet by mouth every 8 hours as needed for nausea",
                      12, "tablets", 0, 4, "temporary",
                      instructions="Patient is post-surgical, urgent fill requested")


def solve_task_h8(state):
    """Prescribe Amlodipine 10mg to preferred pharmacy with hypertension diagnosis."""
    preferred_id = state["currentPatient"]["preferredPharmacyId"]
    pharm = find_entity(state["pharmacies"], id=preferred_id)
    _add_prescription(state, "Amlodipine 10mg tablet",
                      "Take 1 tablet by mouth once daily",
                      30, "tablets", 3, 30, "permanent_rx", pharm["name"],
                      diagnosis=[{"code": "I10", "description": "Essential hypertension"}])


def solve_task_h9(state):
    """Prescribe Escitalopram 10mg to Alto Pharmacy."""
    _add_prescription(state, "Escitalopram 10mg tablet",
                      "Take 1 tablet by mouth once daily in the morning",
                      30, "tablets", 5, 30, "permanent_rx", "Alto Pharmacy")


def solve_task_h10(state):
    """Discontinue Alprazolam (controlled substance) with cancel request."""
    _discontinue_med(state, "Alprazolam 0.5mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", send_cancel=True)


def solve_task_h11(state):
    """Approve the refill with urgent notes (Gabapentin - running low)."""
    _approve_refill(state, "Gabapentin 300mg capsule")


def solve_task_h12(state):
    """Change default pharmacy to UCSF."""
    pharm = find_entity_containing(state["pharmacies"], "name", "UCSF")
    state["settings"]["defaultPharmacyId"] = pharm["id"]


def solve_task_h13(state):
    """Approve the therapeutic substitution change request (not sig clarification)."""
    req = find_entity(state["changeRequests"], originalMedication="Atorvastatin 20mg tablet")
    req["status"] = "approved"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME


def solve_task_h14(state):
    """Document probiotics as OTC."""
    _document_med(state, "Probiotics capsule",
                  "Take 1 capsule by mouth once daily with food")


def solve_task_h15(state):
    """Add bee stings environmental allergy."""
    state["currentPatient"]["allergies"].append({
        "id": f"alg_{state['_nextAlgId']:03d}",
        "allergen": "Bee stings",
        "reaction": "Swelling, anaphylaxis",
        "severity": "Severe",
        "type": "environmental",
        "onsetDate": NOW_DATE,
        "source": "provider-entered"
    })
    state["_nextAlgId"] += 1


def solve_task_h16(state):
    """Edit Lisinopril 10mg template sig for morning dosing."""
    tpl = find_entity(state["rxTemplates"], medicationName="Lisinopril 10mg tablet")
    tpl["sig"] = "Take 1 tablet by mouth once daily in the morning"


def solve_task_h17(state):
    """Discontinue Omeprazole and prescribe Famotidine."""
    _discontinue_med(state, "Omeprazole 20mg capsule", "permanentRxMeds",
                     "I want to discontinue this medication", "Switching to famotidine")
    _add_prescription(state, "Famotidine 20mg tablet",
                      "Take 1 tablet by mouth twice daily",
                      60, "tablets", 3, 30, "permanent_rx", "CVS Pharmacy #4521")


def solve_task_h18(state):
    """Approve Gabapentin refill with twice daily + deny sig clarification."""
    _approve_refill(state, "Gabapentin 300mg capsule",
                    modifications={"sig": "Take 1 capsule by mouth twice daily"})
    req = find_entity(state["changeRequests"], medicationName="Gabapentin 300mg capsule")
    req["status"] = "denied"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME
    req["denyReason"] = "New directions provided with refill approval"


def solve_task_h19(state):
    """Set drug alerts to major+moderate and disable allergy checking."""
    state["settings"]["drugDecisionSupport"]["drugToDrugLevel"] = "major_moderate"
    state["settings"]["drugDecisionSupport"]["drugToAllergyEnabled"] = False


def solve_task_h20(state):
    """Approve all pending CVS refills except Atorvastatin."""
    _approve_refill(state, "Lisinopril 10mg tablet")
    _deny_refill(state, "Atorvastatin 20mg tablet", "Patient needs lipid panel before renewal")
    _approve_refill(state, "Gabapentin 300mg capsule")
    _approve_refill(state, "Omeprazole 20mg capsule")
    _approve_refill(state, "Metoprolol Succinate ER 50mg tablet")


# === HARDENING ROUND 1 (h21-h40) ===

def solve_task_h21(state):
    """Approve Atorvastatin→Rosuvastatin change request + discontinue Atorvastatin."""
    req = find_entity(state["changeRequests"], originalMedication="Atorvastatin 20mg tablet")
    req["status"] = "approved"
    req["processedDate"] = NOW_ISO
    req["processedBy"] = CURRENT_USER_NAME
    _discontinue_med(state, "Atorvastatin 20mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", "Switching to Rosuvastatin per pharmacy request")


def solve_task_h22(state):
    """Approve CVS refills with remaining refills, deny Gabapentin (0 remaining)."""
    _approve_refill(state, "Lisinopril 10mg tablet")
    _approve_refill(state, "Atorvastatin 20mg tablet")
    _approve_refill(state, "Omeprazole 20mg capsule")
    _approve_refill(state, "Metoprolol Succinate ER 50mg tablet")
    _deny_refill(state, "Gabapentin 300mg capsule", "No refills remaining, new prescription required")


def solve_task_h23(state):
    """Discontinue Losartan (prescribed by Dr. Michael Chen)."""
    _discontinue_med(state, "Losartan 50mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication",
                     "Consolidating BP management under one prescriber")


def solve_task_h24(state):
    """Discontinue Ciprofloxacin + change default pharmacy to Rite Aid #3456."""
    _discontinue_med(state, "Ciprofloxacin 500mg tablet", "temporaryMeds",
                     "I want to discontinue this medication")
    state["settings"]["defaultPharmacyId"] = "pharm_005"


def solve_task_h25(state):
    """Approve both change requests."""
    req1 = find_entity(state["changeRequests"], originalMedication="Atorvastatin 20mg tablet")
    req1["status"] = "approved"
    req1["processedDate"] = NOW_ISO
    req1["processedBy"] = CURRENT_USER_NAME
    req2 = find_entity(state["changeRequests"], medicationName="Gabapentin 300mg capsule")
    req2["status"] = "approved"
    req2["processedDate"] = NOW_ISO
    req2["processedBy"] = CURRENT_USER_NAME


def solve_task_h26(state):
    """Approve Omeprazole (GERD med) refill with refills bumped to 5."""
    _approve_refill(state, "Omeprazole 20mg capsule",
                    modifications={"refills": 5})


def solve_task_h27(state):
    """Remove Codeine + Latex allergies, add Tramadol allergy."""
    allergies = state["currentPatient"]["allergies"]
    remove_entity(allergies, allergen="Codeine")
    remove_entity(allergies, allergen="Latex")
    allergies.append({
        "id": f"alg_{state['_nextAlgId']:03d}",
        "allergen": "Tramadol",
        "reaction": "Nausea and dizziness",
        "severity": "Moderate",
        "type": "drug",
        "onsetDate": NOW_DATE,
        "source": "provider-entered"
    })
    state["_nextAlgId"] += 1


def solve_task_h28(state):
    """Discontinue Melatonin (bedtime sleep OTC)."""
    _discontinue_med(state, "Melatonin 3mg tablet", "permanentOtcMeds",
                     "Patient stopped taking medication")


def solve_task_h29(state):
    """Delete all PRN category custom sig shortcuts."""
    state["customSigs"] = [
        s for s in state["customSigs"]
        if s.get("category", "").lower() != "prn"
    ]


def solve_task_h30(state):
    """Discontinue Amlodipine 5mg with cancel + prescribe Amlodipine 10mg."""
    _discontinue_med(state, "Amlodipine 5mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", send_cancel=True)
    _add_prescription(state, "Amlodipine 10mg tablet",
                      "Take 1 tablet by mouth once daily",
                      30, "tablets", 3, 30, "permanent_rx", "CVS Pharmacy #4521",
                      diagnosis=[{"code": "I10", "description": "Essential hypertension"}])


def solve_task_h31(state):
    """Reclassify Losartan (DAW=true) from permanent Rx to temporary."""
    med = remove_entity(state["permanentRxMeds"], medicationName="Losartan 50mg tablet")
    med["classification"] = "temporary"
    state["temporaryMeds"].append(med)


def solve_task_h32(state):
    """Set default pharmacy to Express Scripts Mail Pharmacy."""
    state["settings"]["defaultPharmacyId"] = "pharm_011"


def solve_task_h33(state):
    """Approve Sertraline + Metoprolol refills, deny Atorvastatin."""
    _approve_refill(state, "Sertraline 50mg tablet")
    _approve_refill(state, "Metoprolol Succinate ER 50mg tablet")
    _deny_refill(state, "Atorvastatin 20mg tablet", "Patient needs lab work before renewal")


def solve_task_h34(state):
    """Discontinue Sertraline + prescribe Escitalopram 10mg to Walgreens."""
    _discontinue_med(state, "Sertraline 50mg tablet", "permanentRxMeds",
                     "I want to discontinue this medication", "Switching to Escitalopram")
    _add_prescription(state, "Escitalopram 10mg tablet",
                      "Take 1 tablet by mouth once daily in the morning",
                      30, "tablets", 5, 30, "permanent_rx", "Walgreens #7892")


def solve_task_h35(state):
    """Set default pharmacy to patient's secondary pharmacy (Walgreens #7892)."""
    state["settings"]["defaultPharmacyId"] = "pharm_003"


def solve_task_h36(state):
    """Create Gabapentin 300mg template from active medication details."""
    tpl_id = f"tpl_{state['_nextTplId']:03d}"
    state["rxTemplates"].append({
        "id": tpl_id,
        "medicationName": "Gabapentin 300mg capsule",
        "sig": "Take 1 capsule by mouth three times daily",
        "qty": 90,
        "unit": "capsules",
        "refills": 2,
        "daysSupply": 30,
        "ndc": "59762-5025-01",
        "createdDate": NOW_DATE
    })
    state["_nextTplId"] += 1


def solve_task_h37(state):
    """Med rec + discontinue Prednisone and Ciprofloxacin (expired courses)."""
    state["currentPatient"]["lastReconciledDate"] = NOW_ISO
    _discontinue_med(state, "Prednisone 10mg tablet", "temporaryMeds",
                     "I want to discontinue this medication")
    _discontinue_med(state, "Ciprofloxacin 500mg tablet", "temporaryMeds",
                     "I want to discontinue this medication")


def solve_task_h38(state):
    """Major-only alerts, disable allergy alerts, delete inhalation sigs."""
    state["settings"]["drugDecisionSupport"]["drugToDrugLevel"] = "major_only"
    state["settings"]["drugDecisionSupport"]["drugToAllergyEnabled"] = False
    state["customSigs"] = [
        s for s in state["customSigs"]
        if s.get("category", "").lower() != "inhalation"
    ]


def solve_task_h39(state):
    """Prescribe Metformin 1000mg to preferred pharmacy with diabetes diagnosis."""
    _add_prescription(state, "Metformin 1000mg tablet",
                      "Take 1 tablet by mouth twice daily with meals",
                      60, "tablets", 5, 30, "permanent_rx", "CVS Pharmacy #4521",
                      diagnosis=[{"code": "E11.9", "description": "Type 2 diabetes mellitus"}])


def solve_task_h40(state):
    """Create Doxycycline 100mg template + oral sig shortcut."""
    tpl_id = f"tpl_{state['_nextTplId']:03d}"
    state["rxTemplates"].append({
        "id": tpl_id,
        "medicationName": "Doxycycline 100mg capsule",
        "sig": "Take 1 capsule by mouth twice daily for 14 days",
        "qty": 28,
        "unit": "capsules",
        "refills": 0,
        "daysSupply": 14,
        "ndc": None,
        "createdDate": NOW_DATE
    })
    state["_nextTplId"] += 1
    sig_id = f"sig_{state['_nextSigId']:03d}"
    state["customSigs"].append({
        "id": sig_id,
        "text": "Take 1 capsule by mouth twice daily for 14 days",
        "category": "oral"
    })
    state["_nextSigId"] += 1


# Map task IDs to solve functions
SOLVE_MAP = {}
for _prefix in ["e", "m"]:
    for _i in range(1, 21):
        _task_id = f"task_{_prefix}{_i}"
        _fn_name = f"solve_task_{_prefix}{_i}"
        if _fn_name in globals():
            SOLVE_MAP[_task_id] = globals()[_fn_name]
for _i in range(1, 41):
    _task_id = f"task_h{_i}"
    _fn_name = f"solve_task_h{_i}"
    if _fn_name in globals():
        SOLVE_MAP[_task_id] = globals()[_fn_name]


# ──────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────

def run_single_task(task, server_url, seed_state):
    """Reset → solve → write state → verify. Returns (task_id, passed, message)."""
    task_id = task["id"]

    # 1. Reset
    resp = requests.post(f"{server_url}/api/reset")
    if resp.status_code != 200:
        return task_id, False, f"Reset failed: {resp.status_code}"
    time.sleep(0.3)

    # 2. Clone seed state and apply solve
    state = deepcopy(seed_state)
    solve_fn = SOLVE_MAP.get(task_id)
    if solve_fn is None:
        return task_id, False, f"No solve function for {task_id}"
    try:
        solve_fn(state)
    except Exception as e:
        return task_id, False, f"Solve function error: {e}"

    # 3. Write solved state to server
    resp = requests.put(f"{server_url}/api/state", json=state)
    if resp.status_code != 200:
        return task_id, False, f"PUT state failed: {resp.status_code}"

    # 4. Run verifier
    try:
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
    except Exception as e:
        return task_id, False, f"Verifier exception: {e}"

    return task_id, passed, message


def run_worker(tasks, base_port, worker_id, seed_state):
    """Run tasks sequentially on a dedicated server instance."""
    port = base_port + worker_id
    server_url = f"http://localhost:{port}"

    # Start server
    proc = subprocess.Popen(
        [sys.executable, str(APP_DIR / "server.py"), "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(1.5)

    results = []
    try:
        # Seed the server first
        requests.put(f"{server_url}/api/state", json=seed_state)
        time.sleep(0.3)

        for task in tasks:
            tid, passed, msg = run_single_task(task, server_url, seed_state)
            results.append((tid, passed, msg))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    return results


def main():
    parser = argparse.ArgumentParser(description="Sanity check for real-task verifiers")
    parser.add_argument("--task-id", type=str, default=None, help="Run a single task (or comma-separated list)")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument("--port", type=int, default=8200, help="Base port")
    args = parser.parse_args()

    print("Loading seed data...")
    seed_state = get_seed_state()

    tasks = load_tasks()
    if args.task_id:
        ids = [s.strip() for s in args.task_id.split(",")]
        tasks = [t for t in tasks if t["id"] in ids]
        if not tasks:
            print(f"Task {args.task_id} not found.")
            sys.exit(1)

    print(f"Running sanity check for {len(tasks)} task(s) with {args.workers} worker(s)...\n")

    all_results = []

    if args.workers == 1:
        all_results = run_worker(tasks, args.port, 0, seed_state)
    else:
        # Partition tasks across workers
        chunks = [[] for _ in range(args.workers)]
        for i, task in enumerate(tasks):
            chunks[i % args.workers].append(task)

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(run_worker, chunk, args.port, wid, seed_state): wid
                for wid, chunk in enumerate(chunks) if chunk
            }
            for future in as_completed(futures):
                all_results.extend(future.result())

    # Sort by task ID for consistent output
    difficulty_order = {"e": 0, "m": 1, "h": 2}

    def sort_key(r):
        tid = r[0]
        # task_e1 -> ('e', 1)
        parts = tid.replace("task_", "")
        d = parts[0]
        n = int(parts[1:])
        return (difficulty_order.get(d, 9), n)

    all_results.sort(key=sort_key)

    # Print results
    passed_count = 0
    failed = []
    for tid, passed, msg in all_results:
        status = "\033[32m  PASS\033[0m" if passed else "\033[31m  FAIL\033[0m"
        print(f"{status}  {tid:12s}  {msg}")
        if passed:
            passed_count += 1
        else:
            failed.append(tid)

    print(f"\n{passed_count}/{len(all_results)} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
