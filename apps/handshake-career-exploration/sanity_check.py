#!/usr/bin/env python3
"""
Sanity check for Handshake Career Exploration real tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check.py                     # All tasks, sequential
    python3 sanity_check.py --workers N          # N parallel environments
    python3 sanity_check.py --task-id task_e1    # Single task
    python3 sanity_check.py --port 9500          # Custom base port
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
TASKS_FILE = APP_DIR / "real-tasks.json"

# JS snippet to evaluate data.js and emit the seed state as JSON
_SEED_STATE_JS = """
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    _seedVersion: SEED_DATA_VERSION,
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    employers: JSON.parse(JSON.stringify(EMPLOYERS)),
    jobs: JSON.parse(JSON.stringify(JOBS)),
    feedPosts: JSON.parse(JSON.stringify(FEED_POSTS)),
    events: JSON.parse(JSON.stringify(EVENTS)),
    appointments: JSON.parse(JSON.stringify(APPOINTMENTS)),
    appointmentCategories: JSON.parse(JSON.stringify(APPOINTMENT_CATEGORIES)),
    appointmentStaff: JSON.parse(JSON.stringify(APPOINTMENT_STAFF)),
    availableSlots: JSON.parse(JSON.stringify(AVAILABLE_APPOINTMENT_SLOTS)),
    qaQuestions: JSON.parse(JSON.stringify(QA_QUESTIONS)),
    messages: JSON.parse(JSON.stringify(MESSAGES)),
    schoolLabels: [...SCHOOL_LABELS],
    _nextPostId: 100,
    _nextCommentId: 100,
    _nextAppointmentId: 100,
    _nextQuestionId: 100,
    _nextAnswerId: 100,
};
process.stdout.write(JSON.stringify(state));
"""


# -- helpers ------------------------------------------------------------------

def find_entity(entities, **kwargs):
    """Find an entity by attribute match. Raises if not found."""
    for e in entities:
        if all(e.get(k) == v for k, v in kwargs.items()):
            return e
    raise ValueError(f"Entity not found: {kwargs}")


def find_post(state, post_id):
    return find_entity(state["feedPosts"], id=post_id)


def find_event(state, event_id):
    return find_entity(state["events"], id=event_id)


def find_message(state, message_id):
    return find_entity(state["messages"], id=message_id)


def find_appointment(state, appt_id):
    return find_entity(state["appointments"], id=appt_id)


def find_question(state, question_id):
    return find_entity(state["qaQuestions"], id=question_id)


def find_employer(state, employer_id):
    return find_entity(state["employers"], id=employer_id)


def find_job(state, job_id):
    return find_entity(state["jobs"], id=job_id)


# -- solve functions ----------------------------------------------------------

# === EASY ===

def solve_task_e1(state):
    """Follow Spotify (emp_13)."""
    user = state["currentUser"]
    if "emp_13" not in user["followedEmployerIds"]:
        user["followedEmployerIds"].append("emp_13")
    emp = find_employer(state, "emp_13")
    emp["followCount"] = emp["followCount"] + 1


def solve_task_e2(state):
    """Unfollow Stripe (emp_10)."""
    user = state["currentUser"]
    user["followedEmployerIds"] = [
        eid for eid in user["followedEmployerIds"] if eid != "emp_10"
    ]
    emp = find_employer(state, "emp_10")
    emp["followCount"] = emp["followCount"] - 1


def solve_task_e3(state):
    """Save Microsoft SWE Intern (job_04)."""
    user = state["currentUser"]
    if "job_04" not in user["savedJobIds"]:
        user["savedJobIds"].append("job_04")


def solve_task_e4(state):
    """Unsave Meta ML Engineer Intern (job_07)."""
    user = state["currentUser"]
    user["savedJobIds"] = [jid for jid in user["savedJobIds"] if jid != "job_07"]


def solve_task_e5(state):
    """RSVP to JPMorgan Markets & Trading Panel (evt_08)."""
    evt = find_event(state, "evt_08")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_e6(state):
    """Bookmark Amazon AWS post (post_07)."""
    post = find_post(state, "post_07")
    post["bookmarked"] = True
    user = state["currentUser"]
    if "post_07" not in user["savedPostIds"]:
        user["savedPostIds"].append("post_07")


def solve_task_e7(state):
    """Like Jordan Taylor's startup post (post_12)."""
    post = find_post(state, "post_12")
    post["likes"] = post["likes"] + 1


def solve_task_e8(state):
    """Read Apple Pathways message (msg_08)."""
    msg = find_message(state, "msg_08")
    msg["isRead"] = True


def solve_task_e9(state):
    """Follow Goldman Sachs (emp_06)."""
    user = state["currentUser"]
    if "emp_06" not in user["followedEmployerIds"]:
        user["followedEmployerIds"].append("emp_06")
    emp = find_employer(state, "emp_06")
    emp["followCount"] = emp["followCount"] + 1


def solve_task_e10(state):
    """Save Palantir FDE Intern (job_19)."""
    user = state["currentUser"]
    if "job_19" not in user["savedJobIds"]:
        user["savedJobIds"].append("job_19")


def solve_task_e11(state):
    """RSVP to Google Tech Talk (evt_04)."""
    evt = find_event(state, "evt_04")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_e12(state):
    """Read Meta ML Intern message (msg_03)."""
    msg = find_message(state, "msg_03")
    msg["isRead"] = True


def solve_task_e13(state):
    """Like Anthropic AI safety post (post_05)."""
    post = find_post(state, "post_05")
    post["likes"] = post["likes"] + 1


def solve_task_e14(state):
    """Follow Palantir (emp_17)."""
    user = state["currentUser"]
    if "emp_17" not in user["followedEmployerIds"]:
        user["followedEmployerIds"].append("emp_17")
    emp = find_employer(state, "emp_17")
    emp["followCount"] = emp["followCount"] + 1


def solve_task_e15(state):
    """Bookmark Kevin O'Brien's FAANG post (post_08)."""
    post = find_post(state, "post_08")
    post["bookmarked"] = True
    user = state["currentUser"]
    if "post_08" not in user["savedPostIds"]:
        user["savedPostIds"].append("post_08")


def solve_task_e16(state):
    """RSVP to Salesforce Futureforce (evt_10)."""
    evt = find_event(state, "evt_10")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_e17(state):
    """Unsave Amazon PM Intern (job_24)."""
    user = state["currentUser"]
    user["savedJobIds"] = [jid for jid in user["savedJobIds"] if jid != "job_24"]


def solve_task_e18(state):
    """Mark Nathan Brooks's answer (ans_14) on qa_12 as helpful."""
    q = find_question(state, "qa_12")
    ans = find_entity(q["answers"], id="ans_14")
    ans["helpful"] = ans["helpful"] + 1


def solve_task_e19(state):
    """Like Microsoft Imagine Cup post (post_19)."""
    post = find_post(state, "post_19")
    post["likes"] = post["likes"] + 1


def solve_task_e20(state):
    """Follow Teach For America (emp_18)."""
    user = state["currentUser"]
    if "emp_18" not in user["followedEmployerIds"]:
        user["followedEmployerIds"].append("emp_18")
    emp = find_employer(state, "emp_18")
    emp["followCount"] = emp["followCount"] + 1


# === MEDIUM ===

def solve_task_m1(state):
    """Update bio to mention AI safety."""
    state["currentUser"]["bio"] = "Exploring opportunities in AI safety and alignment research. CS student at Stanford."


def solve_task_m2(state):
    """Add Machine Learning Engineer to preferred roles."""
    ci = state["currentUser"]["careerInterests"]
    if "Machine Learning Engineer" not in ci["roles"]:
        ci["roles"].append("Machine Learning Engineer")


def solve_task_m3(state):
    """Post Q&A question about PM interview prep."""
    q_id = "qa_" + str(state["_nextQuestionId"]).zfill(2)
    state["_nextQuestionId"] += 1
    state["qaQuestions"].insert(0, {
        "id": q_id,
        "authorName": "Maya Chen",
        "authorSchool": state["currentUser"]["school"],
        "authorMajor": state["currentUser"]["major"],
        "authorGradYear": state["currentUser"]["graduationYear"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "question": "What are the best ways to prepare for product management interviews at top tech companies?",
        "status": "pending",
        "createdAt": "2026-03-07T12:00:00Z",
        "views": 0,
        "answers": [],
    })


def solve_task_m4(state):
    """Comment on Jessica Park's post (post_02)."""
    post = find_post(state, "post_02")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "Congrats! Would love to hear more about your experience.",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })


def solve_task_m5(state):
    """Schedule resume review for March 12 at 11 AM, in person."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Resume & Cover Letter",
        "type": "Resume Review",
        "staffId": None,
        "staffName": None,
        "date": "2026-03-12",
        "time": "11:00 AM",
        "duration": 30,
        "medium": "In Person",
        "location": "Career Center",
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })


def solve_task_m6(state):
    """Change career community to Science & Research."""
    state["currentUser"]["careerInterests"]["careerCommunity"] = "Science & Research"


def solve_task_m7(state):
    """Add Boston, MA and Denver, CO to preferred locations."""
    ci = state["currentUser"]["careerInterests"]
    for loc in ["Boston, MA", "Denver, CO"]:
        if loc not in ci["locations"]:
            ci["locations"].append(loc)


def solve_task_m8(state):
    """Remove Finance, add Consulting to industries."""
    ci = state["currentUser"]["careerInterests"]
    ci["industries"] = [ind for ind in ci["industries"] if ind != "Finance"]
    if "Consulting" not in ci["industries"]:
        ci["industries"].append("Consulting")


def solve_task_m9(state):
    """Update LinkedIn URL."""
    state["currentUser"]["linkedinUrl"] = "linkedin.com/in/maya-chen-cs"


def solve_task_m10(state):
    """Create feed post about system design resources."""
    post_id = "post_" + str(state["_nextPostId"])
    state["_nextPostId"] += 1
    state["feedPosts"].insert(0, {
        "id": post_id,
        "authorType": "student",
        "authorId": state["currentUser"]["id"],
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "content": "Here are my favorite system design resources for interview prep: System Design Primer, Grokking the System Design Interview, and Designing Data-Intensive Applications.",
        "audience": "everyone",
        "likes": 0,
        "comments": [],
        "hasImage": False,
        "hasVideo": False,
        "createdAt": "2026-03-07T12:00:00Z",
        "bookmarked": False,
    })


def solve_task_m11(state):
    """Answer qa_04 about virtual career fair attire."""
    q = find_question(state, "qa_04")
    ans_id = "ans_" + str(state["_nextAnswerId"]).zfill(2)
    state["_nextAnswerId"] += 1
    q["answers"].append({
        "id": ans_id,
        "authorName": "Maya Chen",
        "authorSchool": state["currentUser"]["school"],
        "authorMajor": state["currentUser"]["major"],
        "authorGradYear": state["currentUser"]["graduationYear"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "I'd recommend business casual attire - a nice top or blouse works well. Also make sure to test your camera and microphone beforehand!",
        "visibility": "full",
        "status": "pending",
        "createdAt": "2026-03-07T12:00:00Z",
        "helpful": 0,
    })


def solve_task_m12(state):
    """Add comment to appt_01 about LinkedIn headline."""
    appt = find_appointment(state, "appt_01")
    appt["comments"].append({
        "author": state["currentUser"]["fullName"],
        "text": "Can you also help with my LinkedIn headline during our session?",
        "createdAt": "2026-03-07T12:00:00Z",
    })


def solve_task_m13(state):
    """Remove Data Analytics, add Research to job functions."""
    ci = state["currentUser"]["careerInterests"]
    ci["jobFunctions"] = [jf for jf in ci["jobFunctions"] if jf != "Data Analytics"]
    if "Research" not in ci["jobFunctions"]:
        ci["jobFunctions"].append("Research")


def solve_task_m14(state):
    """Change expected graduation date to August 2027."""
    state["currentUser"]["careerInterests"]["expectedGraduationDate"] = "August 2027"


def solve_task_m15(state):
    """Comment on McKinsey post (post_09) about projects."""
    post = find_post(state, "post_09")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "What types of projects can attendees expect to hear about?",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })


def solve_task_m16(state):
    """Save both Anthropic jobs (job_12 already saved, add job_29)."""
    user = state["currentUser"]
    for jid in ["job_12", "job_29"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_m17(state):
    """Add On-campus to job type preferences."""
    ci = state["currentUser"]["careerInterests"]
    if "On-campus" not in ci["jobTypes"]:
        ci["jobTypes"].append("On-campus")


def solve_task_m18(state):
    """Cancel case interview prep appointment (appt_08)."""
    appt = find_appointment(state, "appt_08")
    appt["status"] = "cancelled"


def solve_task_m19(state):
    """Schedule networking strategy appointment for March 17 at 1 PM, virtual."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Networking & Professional Development",
        "type": "Networking Strategy",
        "staffId": None,
        "staffName": None,
        "date": "2026-03-17",
        "time": "1:00 PM",
        "duration": 30,
        "medium": "Virtual on Handshake",
        "location": None,
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })


def solve_task_m20(state):
    """Post semi-anonymous answer to qa_06 about mock interviews."""
    q = find_question(state, "qa_06")
    ans_id = "ans_" + str(state["_nextAnswerId"]).zfill(2)
    state["_nextAnswerId"] += 1
    q["answers"].append({
        "id": ans_id,
        "authorName": "Anonymous",
        "authorSchool": state["currentUser"]["school"],
        "authorMajor": state["currentUser"]["major"],
        "authorGradYear": state["currentUser"]["graduationYear"],
        "authorAvatarColor": "#95A5A6",
        "text": "I also highly recommend practicing with mock system design interviews. Seeing how others approach problems really helps build intuition.",
        "visibility": "semi-anonymous",
        "status": "pending",
        "createdAt": "2026-03-07T12:00:00Z",
        "helpful": 0,
    })


# === HARD ===

def solve_task_h1(state):
    """Follow all consulting firms: McKinsey (emp_04), Deloitte (emp_08), Bain (emp_11)."""
    user = state["currentUser"]
    for emp_id in ["emp_04", "emp_08", "emp_11"]:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
        emp = find_employer(state, emp_id)
        emp["followCount"] = emp["followCount"] + 1


def solve_task_h2(state):
    """Pivot career interests toward consulting."""
    ci = state["currentUser"]["careerInterests"]
    ci["careerCommunity"] = "Business & Finance"
    for role in ["Consultant", "Business Analyst"]:
        if role not in ci["roles"]:
            ci["roles"].append(role)
    if "Consulting" not in ci["industries"]:
        ci["industries"].append("Consulting")
    if "Sales" not in ci["jobFunctions"]:
        ci["jobFunctions"].append("Sales")


def solve_task_h3(state):
    """Save all active Google jobs: job_01, job_02, job_22."""
    user = state["currentUser"]
    for jid in ["job_01", "job_02", "job_22"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h4(state):
    """Unsave closed jobs. job_03 is the only closed job in savedJobIds."""
    user = state["currentUser"]
    closed_ids = set()
    for jid in user["savedJobIds"]:
        try:
            job = find_job(state, jid)
            if job.get("status") == "closed":
                closed_ids.add(jid)
        except ValueError:
            pass
    user["savedJobIds"] = [jid for jid in user["savedJobIds"] if jid not in closed_ids]


def solve_task_h5(state):
    """RSVP to all upcoming virtual events: evt_02, evt_06, evt_07, evt_10."""
    for evt_id in ["evt_02", "evt_06", "evt_07", "evt_10"]:
        evt = find_event(state, evt_id)
        evt["rsvped"] = True
        evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_h6(state):
    """Follow all finance employers: JPMorgan (emp_02), Goldman (emp_06)."""
    user = state["currentUser"]
    for emp_id in ["emp_02", "emp_06"]:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
        emp = find_employer(state, emp_id)
        emp["followCount"] = emp["followCount"] + 1


def solve_task_h7(state):
    """Save all Google and Microsoft internships: job_01, job_02, job_22, job_04, job_23."""
    user = state["currentUser"]
    for jid in ["job_01", "job_02", "job_22", "job_04", "job_23"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h8(state):
    """Schedule grad school advising with Maria Rodriguez and ensure Grad school in postGraduation."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Graduate School",
        "type": "Grad School Advising",
        "staffId": "staff_03",
        "staffName": "Maria Rodriguez",
        "date": "2026-03-18",
        "time": "10:00 AM",
        "duration": 30,
        "medium": "Virtual on Handshake",
        "location": None,
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })
    ci = state["currentUser"]["careerInterests"]
    if "Grad school" not in ci["postGraduation"]:
        ci["postGraduation"].append("Grad school")


def solve_task_h9(state):
    """Bookmark all employer posts from followed companies."""
    seed_followed = ["emp_01", "emp_03", "emp_05", "emp_07", "emp_10", "emp_12", "emp_15"]
    user = state["currentUser"]
    for post in state["feedPosts"]:
        if post.get("authorType") == "employer" and post.get("authorId") in seed_followed:
            post["bookmarked"] = True
            pid = post["id"]
            if pid not in user["savedPostIds"]:
                user["savedPostIds"].append(pid)


def solve_task_h10(state):
    """Read all unread messages and RSVP to Interview Prep workshop (evt_09)."""
    for msg_id in ["msg_01", "msg_03", "msg_06", "msg_08"]:
        msg = find_message(state, msg_id)
        msg["isRead"] = True
    evt = find_event(state, "evt_09")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_h11(state):
    """PM recruiting prep: ensure PM in roles, add Full-time, ensure job_18 and job_24 saved."""
    ci = state["currentUser"]["careerInterests"]
    if "Product Manager" not in ci["roles"]:
        ci["roles"].append("Product Manager")
    if "Full-time" not in ci["jobTypes"]:
        ci["jobTypes"].append("Full-time")
    user = state["currentUser"]
    for jid in ["job_18", "job_24"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h12(state):
    """Replace all locations with Boston, Chicago, Washington DC."""
    state["currentUser"]["careerInterests"]["locations"] = [
        "Boston, MA", "Chicago, IL", "Washington, DC"
    ]


def solve_task_h13(state):
    """Create school-audience post about case interviews and RSVP to McKinsey presentation."""
    post_id = "post_" + str(state["_nextPostId"])
    state["_nextPostId"] += 1
    state["feedPosts"].insert(0, {
        "id": post_id,
        "authorType": "student",
        "authorId": state["currentUser"]["id"],
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "content": "Anyone interested in forming a study group for case interview prep? Let's connect!",
        "audience": "school",
        "likes": 0,
        "comments": [],
        "hasImage": False,
        "hasVideo": False,
        "createdAt": "2026-03-07T12:00:00Z",
        "bookmarked": False,
    })
    evt = find_event(state, "evt_01")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_h14(state):
    """Answer qa_10 about networking, mark ans_07 on qa_05 as helpful."""
    q10 = find_question(state, "qa_10")
    ans_id = "ans_" + str(state["_nextAnswerId"]).zfill(2)
    state["_nextAnswerId"] += 1
    q10["answers"].append({
        "id": ans_id,
        "authorName": "Maya Chen",
        "authorSchool": state["currentUser"]["school"],
        "authorMajor": state["currentUser"]["major"],
        "authorGradYear": state["currentUser"]["graduationYear"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "Start networking with alumni and recruiters early, ideally in August-September of the previous year.",
        "visibility": "full",
        "status": "pending",
        "createdAt": "2026-03-07T12:00:00Z",
        "helpful": 0,
    })
    q05 = find_question(state, "qa_05")
    ans07 = find_entity(q05["answers"], id="ans_07")
    ans07["helpful"] = ans07["helpful"] + 1


def solve_task_h15(state):
    """Cancel all requested appointments: appt_02 and appt_08."""
    for appt_id in ["appt_02", "appt_08"]:
        appt = find_appointment(state, appt_id)
        appt["status"] = "cancelled"


def solve_task_h16(state):
    """Set AI/ML-focused career interests."""
    ci = state["currentUser"]["careerInterests"]
    ci["careerCommunity"] = "Technology"
    ci["roles"] = ["Software Engineer", "Machine Learning Engineer", "Data Scientist", "Research Scientist"]
    ci["industries"] = ["Technology", "Artificial Intelligence"]


def solve_task_h17(state):
    """Follow all employers with AI/ML labeled jobs."""
    user = state["currentUser"]
    aiml_employer_ids = set()
    for job in state["jobs"]:
        if "AI/ML" in job.get("labels", []):
            aiml_employer_ids.add(job["employerId"])
    for emp_id in aiml_employer_ids:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
            emp = find_employer(state, emp_id)
            emp["followCount"] = emp["followCount"] + 1


def solve_task_h18(state):
    """Save all active internships in San Francisco: job_02, job_09, job_12, job_29, job_30."""
    user = state["currentUser"]
    for jid in ["job_02", "job_09", "job_12", "job_29", "job_30"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h19(state):
    """Schedule salary negotiation appointment and update phone."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Networking & Professional Development",
        "type": "Salary Negotiation",
        "staffId": None,
        "staffName": None,
        "date": "2026-03-13",
        "time": "3:00 PM",
        "duration": 30,
        "medium": "Phone",
        "location": None,
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })
    state["currentUser"]["phone"] = "(650) 555-0200"


def solve_task_h20(state):
    """Mark answers about diversity/salary as helpful, bookmark posts by Q&A answerers."""
    # Mark helpful
    q11 = find_question(state, "qa_11")
    ans13 = find_entity(q11["answers"], id="ans_13")
    ans13["helpful"] = ans13["helpful"] + 1

    q05 = find_question(state, "qa_05")
    ans07 = find_entity(q05["answers"], id="ans_07")
    ans07["helpful"] = ans07["helpful"] + 1
    ans08 = find_entity(q05["answers"], id="ans_08")
    ans08["helpful"] = ans08["helpful"] + 1

    # Bookmark posts by Q&A answerers
    user = state["currentUser"]
    for post_id in ["post_12", "post_06", "post_10"]:
        post = find_post(state, post_id)
        post["bookmarked"] = True
        if post_id not in user["savedPostIds"]:
            user["savedPostIds"].append(post_id)


# === HARDENING ROUND 1 ===

def solve_task_h21(state):
    """Save all active Google jobs and RSVP to Google's tech talk.
    Discovery: unread top-match recruiting + tech talk → Google.
    """
    user = state["currentUser"]
    for jid in ["job_01", "job_02", "job_22"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)
    evt = find_event(state, "evt_04")
    evt["rsvped"] = True
    evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_h22(state):
    """Like Nathan Brooks' post (qa_12 liberal arts answerer → post_16)."""
    post = find_post(state, "post_16")
    post["likes"] = post["likes"] + 1


def solve_task_h23(state):
    """Create school post about salary negotiation (most-viewed Q&A: qa_05, 1567 views)."""
    post_id = "post_" + str(state["_nextPostId"])
    state["_nextPostId"] += 1
    state["feedPosts"].insert(0, {
        "id": post_id,
        "authorType": "student",
        "authorId": state["currentUser"]["id"],
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "content": "The most-viewed question in Q&A is about salary negotiation for new grad offers. I highly recommend checking it out - great advice on leveraging competing offers and negotiating total comp!",
        "audience": "school",
        "likes": 0,
        "comments": [],
        "hasImage": False,
        "hasVideo": False,
        "createdAt": "2026-03-07T12:00:00Z",
        "bookmarked": False,
    })


def solve_task_h24(state):
    """RSVP to upcoming events from followed employers: evt_02, evt_04, evt_06."""
    for evt_id in ["evt_02", "evt_04", "evt_06"]:
        evt = find_event(state, evt_id)
        evt["rsvped"] = True
        evt["rsvpCount"] = evt["rsvpCount"] + 1


def solve_task_h25(state):
    """Mark Aisha Mohammed's Q&A answer helpful (NSBE post author → ans_13 on qa_11)."""
    q = find_question(state, "qa_11")
    ans = find_entity(q["answers"], id="ans_13")
    ans["helpful"] = ans["helpful"] + 1


def solve_task_h26(state):
    """Save active internships from private companies + follow unfollowed private companies."""
    user = state["currentUser"]
    # Save active internships from private employers
    for jid in ["job_05", "job_09", "job_11", "job_12", "job_29"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)
    # Follow private companies not yet followed
    for emp_id in ["emp_04", "emp_08", "emp_11", "emp_14", "emp_20"]:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
            emp = find_employer(state, emp_id)
            emp["followCount"] = emp["followCount"] + 1


def solve_task_h27(state):
    """Schedule application review + post Q&A question about follow-up."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Job & Internship Search",
        "type": "Application Review",
        "staffId": None,
        "staffName": None,
        "date": "2026-03-13",
        "time": "10:00 AM",
        "duration": 30,
        "medium": "Phone",
        "location": None,
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })
    q_id = "qa_" + str(state["_nextQuestionId"]).zfill(2)
    state["_nextQuestionId"] += 1
    state["qaQuestions"].insert(0, {
        "id": q_id,
        "authorName": "Maya Chen",
        "authorSchool": state["currentUser"]["school"],
        "authorMajor": state["currentUser"]["major"],
        "authorGradYear": state["currentUser"]["graduationYear"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "question": "What is the best way to follow up after submitting job applications? How long should I wait before reaching out?",
        "status": "pending",
        "createdAt": "2026-03-07T12:00:00Z",
        "views": 0,
        "answers": [],
    })


def solve_task_h28(state):
    """Mark non-anonymous answer on Google interview Q&A as helpful + bookmark Google post."""
    q = find_question(state, "qa_01")
    ans = find_entity(q["answers"], id="ans_01")
    ans["helpful"] = ans["helpful"] + 1
    post = find_post(state, "post_01")
    post["bookmarked"] = True
    user = state["currentUser"]
    if "post_01" not in user["savedPostIds"]:
        user["savedPostIds"].append("post_01")


def solve_task_h29(state):
    """Save active STEM jobs from non-followed employers."""
    user = state["currentUser"]
    for jid in ["job_08", "job_15", "job_16", "job_19", "job_28"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h30(state):
    """Refocus career on finance."""
    ci = state["currentUser"]["careerInterests"]
    ci["careerCommunity"] = "Business & Finance"
    ci["roles"] = ["Financial Analyst", "Business Analyst", "Consultant"]
    ci["industries"] = ["Finance", "Consulting"]
    ci["jobFunctions"] = [jf for jf in ci["jobFunctions"] if jf != "Engineering"]
    if "Finance & Accounting" not in ci["jobFunctions"]:
        ci["jobFunctions"].append("Finance & Accounting")


def solve_task_h31(state):
    """Comment on Marcus Johnson's Stripe post (post_04) + save Stripe job (job_09)."""
    post = find_post(state, "post_04")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "That sounds amazing! How was the onboarding process at Stripe?",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })
    user = state["currentUser"]
    if "job_09" not in user["savedJobIds"]:
        user["savedJobIds"].append("job_09")


def solve_task_h32(state):
    """Save Microsoft jobs (job_04, job_23) + comment on Imagine Cup post (post_19)."""
    user = state["currentUser"]
    for jid in ["job_04", "job_23"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)
    post = find_post(state, "post_19")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "This sounds great! I'm interested in participating in Imagine Cup this year.",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })


def solve_task_h33(state):
    """Comment on David Lee's PM study group post (post_14) found via Saved tab."""
    post = find_post(state, "post_14")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "Thanks for organizing this study group! I'd love to join.",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })


def solve_task_h34(state):
    """Unsave jobs from non-Tech/AI employers: job_03 (Finance), job_18 (Retail)."""
    user = state["currentUser"]
    user["savedJobIds"] = [
        jid for jid in user["savedJobIds"] if jid not in ("job_03", "job_18")
    ]


def solve_task_h35(state):
    """Follow all NY employers + save their active internships."""
    user = state["currentUser"]
    for emp_id in ["emp_02", "emp_04", "emp_06", "emp_08", "emp_13", "emp_18"]:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
            emp = find_employer(state, emp_id)
            emp["followCount"] = emp["followCount"] + 1
    for jid in ["job_05", "job_11", "job_15"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h36(state):
    """Schedule cover letter review with Sarah Thompson + update website URL."""
    appt_id = "appt_" + str(state["_nextAppointmentId"]).zfill(2)
    state["_nextAppointmentId"] += 1
    state["appointments"].append({
        "id": appt_id,
        "category": "Resume & Cover Letter",
        "type": "Cover Letter Review",
        "staffId": "staff_05",
        "staffName": "Sarah Thompson",
        "date": "2026-03-11",
        "time": "1:00 PM",
        "duration": 30,
        "medium": "Virtual on Handshake",
        "location": None,
        "status": "requested",
        "details": "",
        "comments": [],
        "createdAt": "2026-03-07T12:00:00Z",
    })
    state["currentUser"]["websiteUrl"] = "mayachen.design"


def solve_task_h37(state):
    """Set profile visibility to Employers, swap Part-time for Full-time, add LA."""
    state["currentUser"]["profileVisibility"] = "Employers"
    ci = state["currentUser"]["careerInterests"]
    ci["jobTypes"] = [jt for jt in ci["jobTypes"] if jt != "Part-time"]
    if "Full-time" not in ci["jobTypes"]:
        ci["jobTypes"].append("Full-time")
    if "Los Angeles, CA" not in ci["locations"]:
        ci["locations"].append("Los Angeles, CA")


def solve_task_h38(state):
    """Mark Nathan Brooks' Q&A answer helpful (ans_14 on qa_12) + comment on post_16."""
    q = find_question(state, "qa_12")
    ans = find_entity(q["answers"], id="ans_14")
    ans["helpful"] = ans["helpful"] + 1
    post = find_post(state, "post_16")
    comment_id = "cmt_" + str(state["_nextCommentId"])
    state["_nextCommentId"] += 1
    post["comments"].append({
        "id": comment_id,
        "authorName": state["currentUser"]["fullName"],
        "authorSchool": state["currentUser"]["school"],
        "authorAvatarColor": state["currentUser"]["avatarColor"],
        "text": "Thanks for sharing these career fair tips! Really helpful advice.",
        "createdAt": "2026-03-07T12:00:00Z",
        "isAnonymous": False,
    })


def solve_task_h39(state):
    """Like consulting/finance employer posts, follow them, save their active jobs."""
    # Like posts
    post_09 = find_post(state, "post_09")
    post_09["likes"] = post_09["likes"] + 1
    post_15 = find_post(state, "post_15")
    post_15["likes"] = post_15["likes"] + 1
    # Follow employers
    user = state["currentUser"]
    for emp_id in ["emp_02", "emp_04"]:
        if emp_id not in user["followedEmployerIds"]:
            user["followedEmployerIds"].append(emp_id)
            emp = find_employer(state, emp_id)
            emp["followCount"] = emp["followCount"] + 1
    # Save active jobs
    for jid in ["job_05", "job_27"]:
        if jid not in user["savedJobIds"]:
            user["savedJobIds"].append(jid)


def solve_task_h40(state):
    """Read unread messages from Tech employers + bookmark their posts."""
    # Read messages
    for msg_id in ["msg_01", "msg_03", "msg_06", "msg_08"]:
        msg = find_message(state, msg_id)
        msg["isRead"] = True
    # Bookmark posts
    user = state["currentUser"]
    for post_id in ["post_01", "post_03", "post_11", "post_13"]:
        post = find_post(state, post_id)
        post["bookmarked"] = True
        if post_id not in user["savedPostIds"]:
            user["savedPostIds"].append(post_id)


# -- solver registry ----------------------------------------------------------

SOLVERS = {
    "task_e1": solve_task_e1,
    "task_e2": solve_task_e2,
    "task_e3": solve_task_e3,
    "task_e4": solve_task_e4,
    "task_e5": solve_task_e5,
    "task_e6": solve_task_e6,
    "task_e7": solve_task_e7,
    "task_e8": solve_task_e8,
    "task_e9": solve_task_e9,
    "task_e10": solve_task_e10,
    "task_e11": solve_task_e11,
    "task_e12": solve_task_e12,
    "task_e13": solve_task_e13,
    "task_e14": solve_task_e14,
    "task_e15": solve_task_e15,
    "task_e16": solve_task_e16,
    "task_e17": solve_task_e17,
    "task_e18": solve_task_e18,
    "task_e19": solve_task_e19,
    "task_e20": solve_task_e20,
    "task_m1": solve_task_m1,
    "task_m2": solve_task_m2,
    "task_m3": solve_task_m3,
    "task_m4": solve_task_m4,
    "task_m5": solve_task_m5,
    "task_m6": solve_task_m6,
    "task_m7": solve_task_m7,
    "task_m8": solve_task_m8,
    "task_m9": solve_task_m9,
    "task_m10": solve_task_m10,
    "task_m11": solve_task_m11,
    "task_m12": solve_task_m12,
    "task_m13": solve_task_m13,
    "task_m14": solve_task_m14,
    "task_m15": solve_task_m15,
    "task_m16": solve_task_m16,
    "task_m17": solve_task_m17,
    "task_m18": solve_task_m18,
    "task_m19": solve_task_m19,
    "task_m20": solve_task_m20,
    "task_h1": solve_task_h1,
    "task_h2": solve_task_h2,
    "task_h3": solve_task_h3,
    "task_h4": solve_task_h4,
    "task_h5": solve_task_h5,
    "task_h6": solve_task_h6,
    "task_h7": solve_task_h7,
    "task_h8": solve_task_h8,
    "task_h9": solve_task_h9,
    "task_h10": solve_task_h10,
    "task_h11": solve_task_h11,
    "task_h12": solve_task_h12,
    "task_h13": solve_task_h13,
    "task_h14": solve_task_h14,
    "task_h15": solve_task_h15,
    "task_h16": solve_task_h16,
    "task_h17": solve_task_h17,
    "task_h18": solve_task_h18,
    "task_h19": solve_task_h19,
    "task_h20": solve_task_h20,
    "task_h21": solve_task_h21,
    "task_h22": solve_task_h22,
    "task_h23": solve_task_h23,
    "task_h24": solve_task_h24,
    "task_h25": solve_task_h25,
    "task_h26": solve_task_h26,
    "task_h27": solve_task_h27,
    "task_h28": solve_task_h28,
    "task_h29": solve_task_h29,
    "task_h30": solve_task_h30,
    "task_h31": solve_task_h31,
    "task_h32": solve_task_h32,
    "task_h33": solve_task_h33,
    "task_h34": solve_task_h34,
    "task_h35": solve_task_h35,
    "task_h36": solve_task_h36,
    "task_h37": solve_task_h37,
    "task_h38": solve_task_h38,
    "task_h39": solve_task_h39,
    "task_h40": solve_task_h40,
}


# -- server management --------------------------------------------------------

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


def find_free_port(start=9500):
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


# -- task runner ---------------------------------------------------------------

def load_tasks():
    """Load task definitions from real-tasks.json."""
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


# -- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Handshake Career Exploration real-task sanity check"
    )
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
