#!/usr/bin/env python3
"""
Sanity check for Superhuman Mail real tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check.py                     # All tasks, sequential
    python3 sanity_check.py --workers N          # N parallel environments
    python3 sanity_check.py --task-id task_e1    # Single task
    python3 sanity_check.py --port 9600          # Custom base port
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
    emails: JSON.parse(JSON.stringify(EMAILS)),
    contacts: JSON.parse(JSON.stringify(CONTACTS)),
    labels: JSON.parse(JSON.stringify(LABELS)),
    autoLabels: JSON.parse(JSON.stringify(AUTO_LABELS)),
    splits: JSON.parse(JSON.stringify(SPLITS)),
    snippets: JSON.parse(JSON.stringify(SNIPPETS)),
    calendarEvents: JSON.parse(JSON.stringify(CALENDAR_EVENTS)),
    settings: JSON.parse(JSON.stringify(SETTINGS)),
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    recentOpens: JSON.parse(JSON.stringify(RECENT_OPENS)),
    bookingPages: JSON.parse(JSON.stringify(BOOKING_PAGES)),
    _nextEmailId: Math.max(...EMAILS.map(e => e.id)) + 1,
    _nextLabelId: 30,
    _nextSnippetId: 30,
    _nextEventId: 30,
    _nextAutoLabelId: 20,
    _nextSplitId: 20,
    _nextBookingPageId: 10,
};
process.stdout.write(JSON.stringify(state));
"""


# ── helpers ──────────────────────────────────────────────────────────

def find_email_by_subject(state, subject):
    for e in state["emails"]:
        if e["subject"] == subject:
            return e
    raise ValueError(f"Email not found: subject={subject!r}")


def find_email_by_subject_and_sender(state, subject, sender_email):
    for e in state["emails"]:
        if e["subject"] == subject and e["from"]["email"] == sender_email:
            return e
    raise ValueError(f"Email not found: subject={subject!r}, from={sender_email!r}")


def find_label_by_name(state, name):
    for l in state["labels"]:
        if l["name"] == name:
            return l
    raise ValueError(f"Label not found: {name!r}")


def find_snippet_by_name(state, name):
    for s in state["snippets"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Snippet not found: {name!r}")


def find_auto_label_by_name(state, name):
    for al in state["autoLabels"]:
        if al["name"] == name:
            return al
    raise ValueError(f"Auto label not found: {name!r}")


def find_split_by_name(state, name):
    for s in state["splits"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Split not found: {name!r}")


def find_booking_page_by_title(state, title):
    for bp in state["bookingPages"]:
        if bp["title"] == title:
            return bp
    raise ValueError(f"Booking page not found: {title!r}")


# ── solve functions: easy ────────────────────────────────────────────

def solve_task_e1(state):
    """Star the term sheet email from Emily Rodriguez."""
    email = find_email_by_subject_and_sender(
        state, "Re: Series B Term Sheet Discussion", "emily.r@venturelabs.co"
    )
    email["isStarred"] = True


def solve_task_e2(state):
    """Archive the logistics email from Carlos Mendez."""
    email = find_email_by_subject_and_sender(
        state, "Logistics Update - Office Equipment Delivery", "carlos.m@logisticspro.net"
    )
    email["isDone"] = True
    email["isRead"] = True
    email["remindAt"] = None


def solve_task_e3(state):
    """Trash the SurveyMonkey gift card email (already in trash in seed)."""
    email = find_email_by_subject(state, "Complete Your Survey - Win a $500 Gift Card")
    email["isTrashed"] = True


def solve_task_e4(state):
    """Switch to dark mode."""
    state["settings"]["theme"] = "dark"


def solve_task_e5(state):
    """Turn off desktop notifications."""
    state["settings"]["notifications"]["desktop"] = False


def solve_task_e6(state):
    """Disable read receipts."""
    state["settings"]["readReceipts"]["enabled"] = False


def solve_task_e7(state):
    """Turn off Instant Reply."""
    state["settings"]["instantReply"]["enabled"] = False


def solve_task_e8(state):
    """Mark budget email from Priya as unread."""
    email = find_email_by_subject_and_sender(
        state, "Budget Approval Needed - Marketing Campaign", "priya.sharma@acmecorp.com"
    )
    email["isRead"] = False


def solve_task_e9(state):
    """Unstar FY2026 Budget Summary."""
    email = find_email_by_subject(state, "FY2026 Budget Summary")
    email["isStarred"] = False


def solve_task_e10(state):
    """Turn off Smart Send."""
    state["settings"]["smartSend"]["enabled"] = False


def solve_task_e11(state):
    """Disable keyboard shortcuts."""
    state["settings"]["keyboard"]["shortcuts"] = False


def solve_task_e12(state):
    """Delete the Out of Office snippet."""
    state["snippets"] = [s for s in state["snippets"] if s["name"] != "Out of Office"]


def solve_task_e13(state):
    """Change swipe left action to Trash."""
    state["settings"]["swipeLeft"] = "trash"


def solve_task_e14(state):
    """Turn off sound notifications."""
    state["settings"]["notifications"]["sound"] = False


def solve_task_e15(state):
    """Disable auto archive."""
    state["settings"]["autoArchive"]["enabled"] = False


def solve_task_e16(state):
    """Deactivate Product Demo booking page."""
    bp = find_booking_page_by_title(state, "Product Demo")
    bp["isActive"] = False


def solve_task_e17(state):
    """Disable auto drafts."""
    state["settings"]["autoDrafts"]["enabled"] = False


def solve_task_e18(state):
    """Switch meeting link provider to Google Meet."""
    state["settings"]["meetingLink"]["provider"] = "google-meet"


def solve_task_e19(state):
    """Turn off auto-add meeting links."""
    state["settings"]["meetingLink"]["autoAdd"] = False


def solve_task_e20(state):
    """Disable calendar alerts."""
    state["settings"]["notifications"]["calendarAlerts"] = False


# ── solve functions: medium ──────────────────────────────────────────

def solve_task_m1(state):
    """Add Urgent label to Sarah Chen's roadmap email."""
    label = find_label_by_name(state, "Urgent")
    email = find_email_by_subject_and_sender(
        state, "Q2 Product Roadmap - Final Review", "sarah.chen@acmecorp.com"
    )
    if label["id"] not in email["labels"]:
        email["labels"].append(label["id"])


def solve_task_m2(state):
    """Remove Marketing label from Marcus Williams' brand assets email."""
    label = find_label_by_name(state, "Marketing")
    email = find_email_by_subject_and_sender(
        state, "New Brand Assets - Review Needed", "marcus.w@designhub.io"
    )
    email["labels"] = [l for l in email["labels"] if l != label["id"]]


def solve_task_m3(state):
    """Create a new label called 'Partnerships' with teal color."""
    label_id = "label_" + str(state.get("_nextLabelId", 30))
    state["_nextLabelId"] = state.get("_nextLabelId", 30) + 1
    state["labels"].append({
        "id": label_id,
        "name": "Partnerships",
        "type": "user",
        "color": "#009688"
    })


def solve_task_m4(state):
    """Set reminder on Kevin Zhao's quantum computing email for March 9 (next Monday)."""
    email = find_email_by_subject_and_sender(
        state, "Quantum Computing Integration Prototype", "kevin.zhao@quantumlab.tech"
    )
    email["remindAt"] = "2026-03-09T09:00:00.000Z"
    email["isRead"] = True


def solve_task_m5(state):
    """Move CryptoGains spam email back to inbox."""
    email = find_email_by_subject(state, "Make $50K/day with this ONE trick!")
    email["isSpam"] = False


def solve_task_m6(state):
    """Create 'Project Update' snippet."""
    snip_id = "snip_" + str(state.get("_nextSnippetId", 30))
    state["_nextSnippetId"] = state.get("_nextSnippetId", 30) + 1
    state["snippets"].append({
        "id": snip_id,
        "name": "Project Update",
        "body": "Hi {first_name}, here is the latest update on {project_name}. Let me know if you have questions.",
        "variables": ["first_name", "project_name"],
        "isShared": False,
        "author": "Alex Morgan",
        "authorId": "user_1",
        "createdAt": "2026-03-07T12:00:00Z",
        "metrics": {"sends": 0, "openRate": 0, "responseRate": 0}
    })


def solve_task_m7(state):
    """Switch auto reminders to 'All external' mode."""
    state["settings"]["autoReminders"]["mode"] = "external"


def solve_task_m8(state):
    """Change primary timezone to Pacific Time."""
    state["settings"]["timezone"] = "America/Los_Angeles"


def solve_task_m9(state):
    """Send email to David Kim about scheduling partnership call."""
    email_id = state.get("_nextEmailId", 200)
    state["_nextEmailId"] = email_id + 1
    state["emails"].insert(0, {
        "id": email_id,
        "threadId": "thread_" + str(email_id),
        "from": {"name": "Alex Morgan", "email": "alex.morgan@acmecorp.com"},
        "to": [{"name": "David Kim", "email": "david.kim@financeplus.com"}],
        "cc": [], "bcc": [],
        "subject": "Partnership Call - Next Week",
        "snippet": "Hi David, let's schedule our partnership call for next week.",
        "body": "Hi David, let's schedule our partnership call for next week. Looking forward to discussing the integration.",
        "date": "2026-03-07T12:00:00Z",
        "isRead": True, "isStarred": False, "isDone": False,
        "isTrashed": False, "isSpam": False, "isDraft": False,
        "labels": [], "hasAttachments": False, "attachments": [],
        "splitCategory": "important", "remindAt": None,
        "readReceipt": {"opened": False},
        "autoLabel": None, "replyDraftingTeammate": None, "threadMessages": None
    })


def solve_task_m10(state):
    """Create 'Team Lunch' calendar event on March 13, 12-1pm at Café Roma."""
    evt_id = "evt_" + str(state.get("_nextEventId", 30))
    state["_nextEventId"] = state.get("_nextEventId", 30) + 1
    state["calendarEvents"].append({
        "id": evt_id,
        "title": "Team Lunch",
        "date": "2026-03-13",
        "startTime": "12:00",
        "endTime": "13:00",
        "location": "Café Roma",
        "description": "",
        "attendees": [],
        "meetingLink": None,
        "isAllDay": False,
        "calendarId": "work",
        "organizer": "alex.morgan@acmecorp.com",
        "status": "confirmed",
        "color": "#6C4FF7"
    })


def solve_task_m11(state):
    """Delete the 'Receipts' label."""
    label = find_label_by_name(state, "Receipts")
    label_id = label["id"]
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]
    for e in state["emails"]:
        e["labels"] = [l for l in e["labels"] if l != label_id]


def solve_task_m12(state):
    """Create custom auto label 'Design Review' matching subject 'design'."""
    al_id = "al_" + str(state.get("_nextAutoLabelId", 20))
    state["_nextAutoLabelId"] = state.get("_nextAutoLabelId", 20) + 1
    state["autoLabels"].append({
        "id": al_id,
        "name": "Design Review",
        "type": "custom",
        "enabled": True,
        "criteria": {"subject": "design"}
    })


def solve_task_m13(state):
    """Disable Shipping Update auto label (already disabled in seed)."""
    al = find_auto_label_by_name(state, "Shipping Update")
    al["enabled"] = False


def solve_task_m14(state):
    """Share Meeting Follow-up snippet (already shared in seed)."""
    snip = find_snippet_by_name(state, "Meeting Follow-up")
    snip["isShared"] = True


def solve_task_m15(state):
    """Update signature: 'VP of Product' → 'Chief Product Officer'."""
    sig = state["settings"]["signature"]
    state["settings"]["signature"] = sig.replace("VP of Product", "Chief Product Officer")


def solve_task_m16(state):
    """Change swipe right action to Star."""
    state["settings"]["swipeRight"] = "star"


def solve_task_m17(state):
    """Move Ana Gutierrez's sponsorship email to trash."""
    email = find_email_by_subject_and_sender(
        state, "Global Health Initiative - Sponsorship Request", "ana.g@globalhealth.org"
    )
    email["isTrashed"] = True
    email["isDone"] = False
    email["remindAt"] = None


def solve_task_m18(state):
    """Activate Quick Sync booking page."""
    bp = find_booking_page_by_title(state, "Quick Sync")
    bp["isActive"] = True


def solve_task_m19(state):
    """Change calendar alert timing to 15 minutes."""
    state["settings"]["notifications"]["alertMinutes"] = 15


def solve_task_m20(state):
    """Set secondary timezone to none."""
    state["settings"]["secondaryTimezone"] = ""


# ── solve functions: hard ────────────────────────────────────────────

def solve_task_h1(state):
    """Label FinancePlus + QuantumLab emails as 'Clients'."""
    label = find_label_by_name(state, "Clients")
    lid = label["id"]
    e1 = find_email_by_subject(state, "Partnership Opportunity - FinancePlus x Acme")
    e2 = find_email_by_subject(state, "Quantum Computing Integration Prototype")
    for e in [e1, e2]:
        if lid not in e["labels"]:
            e["labels"].append(lid)


def solve_task_h2(state):
    """Archive all unread emails in Important inbox split."""
    for e in state["emails"]:
        if (not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
                and not e["isDraft"] and e["remindAt"] is None
                and e["splitCategory"] == "important" and not e["isRead"]):
            e["isDone"] = True
            e["isRead"] = True
            e["remindAt"] = None


def solve_task_h3(state):
    """Create 'Follow Up' label and apply to O'Brien + Wu emails."""
    label_id = "label_" + str(state.get("_nextLabelId", 30))
    state["_nextLabelId"] = state.get("_nextLabelId", 30) + 1
    state["labels"].append({
        "id": label_id, "name": "Follow Up", "type": "user", "color": "#FF9800"
    })
    e1 = find_email_by_subject_and_sender(
        state, "Re: Vendor Agreement - CloudScale", "james.obrien@legalwise.com"
    )
    e2 = find_email_by_subject_and_sender(
        state, "Research Collaboration Proposal", "jennifer.wu@biomedresearch.com"
    )
    for e in [e1, e2]:
        if label_id not in e["labels"]:
            e["labels"].append(label_id)


def solve_task_h4(state):
    """Dark mode + disable desktop notifications + disable sound."""
    state["settings"]["theme"] = "dark"
    state["settings"]["notifications"]["desktop"] = False
    state["settings"]["notifications"]["sound"] = False


def solve_task_h5(state):
    """Unsubscribe from Morning Brew."""
    email = find_email_by_subject_and_sender(
        state, "Morning Brew - Markets surge on Fed pivot signals", "crew@morningbrew.com"
    )
    email["isDone"] = True
    email["isRead"] = True
    if "blockedSenders" not in state["settings"]:
        state["settings"]["blockedSenders"] = []
    if "crew@morningbrew.com" not in state["settings"]["blockedSenders"]:
        state["settings"]["blockedSenders"].append("crew@morningbrew.com")


def solve_task_h6(state):
    """Delete (trash) all three spam emails."""
    spam_subjects = [
        "URGENT: Inheritance Notification - $4.5M USD",
        "Make $50K/day with this ONE trick!",
        "Limited Time: 90% Off Premium Products",
    ]
    for e in state["emails"]:
        if e["subject"] in spam_subjects:
            e["isTrashed"] = True
            e["isDone"] = False
            e["remindAt"] = None


def solve_task_h7(state):
    """Create booking page 'Strategy Session', 60 min, Google Meet, Mon-Thu 1-5pm."""
    bp_id = "bp_" + str(state.get("_nextBookingPageId", 10))
    state["_nextBookingPageId"] = state.get("_nextBookingPageId", 10) + 1
    state["bookingPages"].append({
        "id": bp_id,
        "title": "Strategy Session",
        "duration": 60,
        "location": "Google Meet",
        "description": "",
        "availability": {
            "days": ["Mon", "Tue", "Wed", "Thu"],
            "startTime": "13:00",
            "endTime": "17:00"
        },
        "link": "https://cal.superhuman.com/alex/strategy-session",
        "isActive": True
    })


def solve_task_h8(state):
    """Send email to Sophie Laurent accepting EuroDesign speaking invitation."""
    email_id = state.get("_nextEmailId", 200)
    state["_nextEmailId"] = email_id + 1
    state["emails"].insert(0, {
        "id": email_id,
        "threadId": "thread_" + str(email_id),
        "from": {"name": "Alex Morgan", "email": "alex.morgan@acmecorp.com"},
        "to": [{"name": "Sophie Laurent", "email": "sophie.l@eurodesign.fr"}],
        "cc": [], "bcc": [],
        "subject": "Re: EuroDesign Conference - Speaker Invitation",
        "snippet": "Hi Sophie, I'd be happy to accept the invitation to speak at EuroDesign Summit.",
        "body": "Hi Sophie,\n\nI'd be happy to accept the invitation to speak at EuroDesign Summit 2026. The proposed topic works well for me.\n\nLooking forward to it!\n\nBest,\nAlex",
        "date": "2026-03-07T12:00:00Z",
        "isRead": True, "isStarred": False, "isDone": False,
        "isTrashed": False, "isSpam": False, "isDraft": False,
        "labels": [], "hasAttachments": False, "attachments": [],
        "splitCategory": "important", "remindAt": None,
        "readReceipt": {"opened": False},
        "autoLabel": None, "replyDraftingTeammate": None, "threadMessages": None
    })


def solve_task_h9(state):
    """Archive Tom + Carlos emails, star CloudScale contract."""
    e1 = find_email_by_subject_and_sender(
        state, "Re: Infrastructure Migration Plan", "tom.bradley@acmecorp.com"
    )
    e1["isDone"] = True
    e1["isRead"] = True
    e1["remindAt"] = None

    e2 = find_email_by_subject_and_sender(
        state, "Logistics Update - Office Equipment Delivery", "carlos.m@logisticspro.net"
    )
    e2["isDone"] = True
    e2["isRead"] = True
    e2["remindAt"] = None

    e3 = find_email_by_subject_and_sender(
        state, "CloudScale Contract - Ready to Sign", "michael.f@cloudscale.dev"
    )
    e3["isStarred"] = True


def solve_task_h10(state):
    """Create auto label 'Legal' from legalwise.com, disable Support Ticket."""
    al_id = "al_" + str(state.get("_nextAutoLabelId", 20))
    state["_nextAutoLabelId"] = state.get("_nextAutoLabelId", 20) + 1
    state["autoLabels"].append({
        "id": al_id,
        "name": "Legal",
        "type": "custom",
        "enabled": True,
        "criteria": {"from": "legalwise.com"}
    })
    al = find_auto_label_by_name(state, "Support Ticket")
    al["enabled"] = False


def solve_task_h11(state):
    """Clear reminders on all snoozed emails."""
    for e in state["emails"]:
        if e["remindAt"] is not None:
            e["remindAt"] = None


def solve_task_h12(state):
    """Pacific timezone, no secondary timezone, Microsoft Teams."""
    state["settings"]["timezone"] = "America/Los_Angeles"
    state["settings"]["secondaryTimezone"] = ""
    state["settings"]["meetingLink"]["provider"] = "teams"


def solve_task_h13(state):
    """Create 'Weekly Review' event on March 13, 4-5pm, Zoom, with Sarah + Nate."""
    evt_id = "evt_" + str(state.get("_nextEventId", 30))
    state["_nextEventId"] = state.get("_nextEventId", 30) + 1
    state["calendarEvents"].append({
        "id": evt_id,
        "title": "Weekly Review",
        "date": "2026-03-13",
        "startTime": "16:00",
        "endTime": "17:00",
        "location": "Zoom",
        "description": "",
        "attendees": ["sarah.chen@acmecorp.com", "nate.patel@acmecorp.com"],
        "meetingLink": None,
        "isAllDay": False,
        "calendarId": "work",
        "organizer": "alex.morgan@acmecorp.com",
        "status": "confirmed",
        "color": "#6C4FF7"
    })


def solve_task_h14(state):
    """Delete Decline Politely + Quick Check-in, unshare Introduction."""
    state["snippets"] = [
        s for s in state["snippets"]
        if s["name"] not in ("Decline Politely", "Quick Check-in")
    ]
    snip = find_snippet_by_name(state, "Introduction")
    snip["isShared"] = False


def solve_task_h15(state):
    """Remove Engineering label from all emails."""
    label = find_label_by_name(state, "Engineering")
    lid = label["id"]
    for e in state["emails"]:
        e["labels"] = [l for l in e["labels"] if l != lid]


def solve_task_h16(state):
    """Disable auto reminders, auto drafts, and Smart Send."""
    state["settings"]["autoReminders"]["enabled"] = False
    state["settings"]["autoDrafts"]["enabled"] = False
    state["settings"]["smartSend"]["enabled"] = False


def solve_task_h17(state):
    """Star and archive Sarah's roadmap, Emily's term sheet, Priya's budget emails."""
    subjects = [
        ("Q2 Product Roadmap - Final Review", "sarah.chen@acmecorp.com"),
        ("Re: Series B Term Sheet Discussion", "emily.r@venturelabs.co"),
        ("Budget Approval Needed - Marketing Campaign", "priya.sharma@acmecorp.com"),
    ]
    for subj, sender in subjects:
        e = find_email_by_subject_and_sender(state, subj, sender)
        e["isStarred"] = True
        e["isDone"] = True
        e["isRead"] = True
        e["remindAt"] = None


def solve_task_h18(state):
    """Create 'NDA Request' snippet, shared with team."""
    snip_id = "snip_" + str(state.get("_nextSnippetId", 30))
    state["_nextSnippetId"] = state.get("_nextSnippetId", 30) + 1
    state["snippets"].append({
        "id": snip_id,
        "name": "NDA Request",
        "body": "Hi {first_name}, please find the NDA attached for {company_name}. Kindly review and sign by {deadline}.",
        "variables": ["first_name", "company_name", "deadline"],
        "isShared": True,
        "author": "Alex Morgan",
        "authorId": "user_1",
        "createdAt": "2026-03-07T12:00:00Z",
        "metrics": {"sends": 0, "openRate": 0, "responseRate": 0}
    })


def solve_task_h19(state):
    """Delete Feeds and Notifications custom splits."""
    state["splits"] = [s for s in state["splits"] if s["name"] not in ("Feeds", "Notifications")]


def solve_task_h20(state):
    """Move all emails labeled 'Travel' to Done."""
    label = find_label_by_name(state, "Travel")
    lid = label["id"]
    for e in state["emails"]:
        if lid in e["labels"]:
            e["isDone"] = True
            e["isRead"] = True
            e["remindAt"] = None


# ── solver registry ──────────────────────────────────────────────────

SOLVERS = {}
for _prefix in ("e", "m", "h"):
    for _i in range(1, 21):
        _key = f"task_{_prefix}{_i}"
        _fn_name = f"solve_{_key}"
        if _fn_name in globals():
            SOLVERS[_key] = globals()[_fn_name]


# ── infrastructure ──────────────────────────────────────────────────

def generate_seed_state():
    """Evaluate data.js through Node.js to get the seed state as Python dict."""
    data_js_path = APP_DIR / "js" / "data.js"
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, str(data_js_path)],
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
    """Start the Superhuman server on the given port."""
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


# ── task runner ──────────────────────────────────────────────────────

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


# ── main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Superhuman real-task sanity check")
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
