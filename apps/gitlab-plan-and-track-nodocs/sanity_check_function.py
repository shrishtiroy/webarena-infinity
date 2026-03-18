#!/usr/bin/env python3
"""Sanity check for GitLab Plan & Track function-test tasks."""
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

# ---------------------------------------------------------------------------
# Seed state generation — evaluate data.js via Node to get the exact same
# seed state the browser would produce.
# ---------------------------------------------------------------------------
_SEED_STATE_JS = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    _seedVersion: SEED_DATA_VERSION,
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    users: JSON.parse(JSON.stringify(USERS)),
    labels: JSON.parse(JSON.stringify(LABELS)),
    milestones: JSON.parse(JSON.stringify(MILESTONES)),
    iterationCadences: JSON.parse(JSON.stringify(ITERATION_CADENCES)),
    iterations: JSON.parse(JSON.stringify(ITERATIONS)),
    epics: JSON.parse(JSON.stringify(EPICS)),
    issues: JSON.parse(JSON.stringify(ISSUES)),
    boards: JSON.parse(JSON.stringify(BOARDS)),
    issueTemplates: JSON.parse(JSON.stringify(ISSUE_TEMPLATES)),
    notificationSettings: JSON.parse(JSON.stringify(NOTIFICATION_SETTINGS)),
    notificationFeed: JSON.parse(JSON.stringify(NOTIFICATION_FEED)),
    _nextIssueId: Math.max(...ISSUES.map(i => i.id)) + 1,
    _nextLabelId: Math.max(...LABELS.map(l => l.id)) + 1,
    _nextMilestoneId: Math.max(...MILESTONES.map(m => m.id)) + 1,
    _nextIterationId: Math.max(...ITERATIONS.map(i => i.id)) + 1,
    _nextEpicId: Math.max(...EPICS.map(e => e.id)) + 1,
    _nextBoardId: Math.max(...BOARDS.map(b => b.id)) + 1,
    _nextBoardListId: Math.max(...BOARDS.flatMap(b => b.lists.map(l => l.id))) + 1,
    _nextCommentId: 1000,
    _nextNotificationId: Math.max(...NOTIFICATION_FEED.map(n => n.id)) + 1
};
process.stdout.write(JSON.stringify(state));
"""


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_entity(entities, **kwargs):
    """Find an entity by attribute match. Raises if not found."""
    for e in entities:
        if all(e.get(k) == v for k, v in kwargs.items()):
            return e
    raise ValueError(f"Entity not found: {kwargs}")


def find_issue_by_iid(state, iid):
    return find_entity(state["issues"], iid=iid)


def find_label_by_name(state, name):
    return find_entity(state["labels"], name=name)


def find_milestone_by_title(state, title):
    return find_entity(state["milestones"], title=title)


def find_iteration_by_title(state, title):
    return find_entity(state["iterations"], title=title)


def find_epic_by_title(state, title):
    return find_entity(state["epics"], title=title)


def find_user_by_name(state, name):
    return find_entity(state["users"], name=name)


def find_board_by_name(state, name):
    return find_entity(state["boards"], name=name)


# ---------------------------------------------------------------------------
# Solve functions — one per task, derived from the corresponding verifier.
# Each mutates `state` in place.
# ---------------------------------------------------------------------------

def solve_task_1(state):
    """Create a new issue titled 'Implement dark mode toggle'."""
    max_iid = max(i["iid"] for i in state["issues"])
    state["issues"].insert(0, {
        "id": state["_nextIssueId"],
        "iid": max_iid + 1,
        "title": "Implement dark mode toggle",
        "description": "",
        "state": "opened",
        "type": "issue",
        "authorId": state["currentUser"]["id"],
        "assignees": [],
        "labels": [],
        "milestoneId": None,
        "iterationId": None,
        "epicId": None,
        "weight": None,
        "dueDate": None,
        "confidential": False,
        "timeEstimate": None,
        "timeSpent": 0,
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
        "closedAt": None,
        "closedBy": None,
        "upvotes": 0,
        "downvotes": 0,
        "subscribed": True,
        "relatedIssues": [],
        "activities": [],
    })
    state["_nextIssueId"] += 1


def solve_task_2(state):
    """Create a new incident titled 'Production API timeout errors'."""
    max_iid = max(i["iid"] for i in state["issues"])
    state["issues"].insert(0, {
        "id": state["_nextIssueId"],
        "iid": max_iid + 1,
        "title": "Production API timeout errors",
        "description": "",
        "state": "opened",
        "type": "incident",
        "authorId": state["currentUser"]["id"],
        "assignees": [],
        "labels": [],
        "milestoneId": None,
        "iterationId": None,
        "epicId": None,
        "weight": None,
        "dueDate": None,
        "confidential": False,
        "timeEstimate": None,
        "timeSpent": 0,
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
        "closedAt": None,
        "closedBy": None,
        "upvotes": 0,
        "downvotes": 0,
        "subscribed": True,
        "relatedIssues": [],
        "activities": [],
    })
    state["_nextIssueId"] += 1


def solve_task_3(state):
    """Create a new task with weight 3."""
    max_iid = max(i["iid"] for i in state["issues"])
    state["issues"].insert(0, {
        "id": state["_nextIssueId"],
        "iid": max_iid + 1,
        "title": "Update CI pipeline configuration",
        "description": "",
        "state": "opened",
        "type": "task",
        "authorId": state["currentUser"]["id"],
        "assignees": [],
        "labels": [],
        "milestoneId": None,
        "iterationId": None,
        "epicId": None,
        "weight": 3,
        "dueDate": None,
        "confidential": False,
        "timeEstimate": None,
        "timeSpent": 0,
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
        "closedAt": None,
        "closedBy": None,
        "upvotes": 0,
        "downvotes": 0,
        "subscribed": True,
        "relatedIssues": [],
        "activities": [],
    })
    state["_nextIssueId"] += 1


def solve_task_4(state):
    """Close issue #101."""
    issue = find_issue_by_iid(state, 101)
    issue["state"] = "closed"
    issue["closedAt"] = "2026-03-18T12:00:00.000Z"
    issue["closedBy"] = state["currentUser"]["id"]


def solve_task_5(state):
    """Reopen issue #111."""
    issue = find_issue_by_iid(state, 111)
    issue["state"] = "opened"
    issue["closedAt"] = None
    issue["closedBy"] = None


def solve_task_6(state):
    """Change title of issue #105."""
    issue = find_issue_by_iid(state, 105)
    issue["title"] = "Add mobile-first responsive navigation"


def solve_task_7(state):
    """Edit description of issue #119."""
    issue = find_issue_by_iid(state, 119)
    issue["description"] = (issue.get("description") or "") + "\n\nFix: Wrap all field values in double quotes before writing to CSV."


def solve_task_8(state):
    """Create issue with Bug Report template."""
    max_iid = max(i["iid"] for i in state["issues"])
    template = next(t for t in state["issueTemplates"] if t["name"] == "Bug Report")
    state["issues"].insert(0, {
        "id": state["_nextIssueId"],
        "iid": max_iid + 1,
        "title": "Login form does not validate email format",
        "description": template["content"],
        "state": "opened",
        "type": "issue",
        "authorId": state["currentUser"]["id"],
        "assignees": [],
        "labels": [],
        "milestoneId": None,
        "iterationId": None,
        "epicId": None,
        "weight": None,
        "dueDate": None,
        "confidential": False,
        "timeEstimate": None,
        "timeSpent": 0,
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
        "closedAt": None,
        "closedBy": None,
        "upvotes": 0,
        "downvotes": 0,
        "subscribed": True,
        "relatedIssues": [],
        "activities": [],
    })
    state["_nextIssueId"] += 1


def solve_task_9(state):
    """Assign David Thompson to issue #107."""
    issue = find_issue_by_iid(state, 107)
    david = find_user_by_name(state, "David Thompson")
    if david["id"] not in issue["assignees"]:
        issue["assignees"].append(david["id"])


def solve_task_10(state):
    """Add tech-debt label to issue #109."""
    issue = find_issue_by_iid(state, 109)
    label = find_label_by_name(state, "tech-debt")
    if label["id"] not in issue["labels"]:
        issue["labels"].append(label["id"])


def solve_task_11(state):
    """Set milestone v4.3 Release on issue #120."""
    issue = find_issue_by_iid(state, 120)
    ms = find_milestone_by_title(state, "v4.3 Release")
    issue["milestoneId"] = ms["id"]


def solve_task_12(state):
    """Set iteration Sprint 27 on issue #116."""
    issue = find_issue_by_iid(state, 116)
    iteration = find_iteration_by_title(state, "Sprint 27")
    issue["iterationId"] = iteration["id"]


def solve_task_13(state):
    """Set epic on issue #120."""
    issue = find_issue_by_iid(state, 120)
    epic = find_epic_by_title(state, "Accessibility Compliance (WCAG 2.1 AA)")
    issue["epicId"] = epic["id"]


def solve_task_14(state):
    """Set weight 7 on issue #117."""
    issue = find_issue_by_iid(state, 117)
    issue["weight"] = 7


def solve_task_15(state):
    """Set due date on issue #123."""
    issue = find_issue_by_iid(state, 123)
    issue["dueDate"] = "2026-04-10"


def solve_task_16(state):
    """Mark issue #123 confidential."""
    issue = find_issue_by_iid(state, 123)
    issue["confidential"] = True


def solve_task_17(state):
    """Unsubscribe from issue #101."""
    issue = find_issue_by_iid(state, 101)
    issue["subscribed"] = False


def solve_task_18(state):
    """Remove Marcus Johnson from issue #101."""
    issue = find_issue_by_iid(state, 101)
    marcus = find_user_by_name(state, "Marcus Johnson")
    issue["assignees"] = [a for a in issue["assignees"] if a != marcus["id"]]


def solve_task_19(state):
    """Add comment to issue #106."""
    issue = find_issue_by_iid(state, 106)
    issue["activities"].append({
        "id": state["_nextCommentId"],
        "type": "comment",
        "authorId": state["currentUser"]["id"],
        "content": "This needs to be prioritized for the next sprint",
        "createdAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextCommentId"] += 1


def solve_task_20(state):
    """Assign Lisa Wang to issue #117 via quick action."""
    issue = find_issue_by_iid(state, 117)
    lisa = find_user_by_name(state, "Lisa Wang")
    if lisa["id"] not in issue["assignees"]:
        issue["assignees"].append(lisa["id"])


def solve_task_21(state):
    """Close issue #119 via /close quick action."""
    issue = find_issue_by_iid(state, 119)
    issue["state"] = "closed"
    issue["closedAt"] = "2026-03-18T12:00:00.000Z"
    issue["closedBy"] = state["currentUser"]["id"]


def solve_task_22(state):
    """Set weight 4 on issue #116 via /weight quick action."""
    issue = find_issue_by_iid(state, 116)
    issue["weight"] = 4


def solve_task_23(state):
    """Set time estimate to 16h on issue #117."""
    issue = find_issue_by_iid(state, 117)
    issue["timeEstimate"] = 16 * 3600  # 57600 seconds


def solve_task_24(state):
    """Log 2h30m on issue #115."""
    issue = find_issue_by_iid(state, 115)
    issue["timeSpent"] = (issue.get("timeSpent") or 0) + 9000  # 2h30m = 9000s


def solve_task_25(state):
    """Add issue #121 as blocking related issue on #115."""
    issue_115 = find_issue_by_iid(state, 115)
    issue_121 = find_issue_by_iid(state, 121)
    issue_115["relatedIssues"].append({"issueId": issue_121["id"], "linkType": "blocks"})
    issue_121["relatedIssues"].append({"issueId": issue_115["id"], "linkType": "is_blocked_by"})


def solve_task_26(state):
    """Add relates_to link between #117 and #115."""
    issue_117 = find_issue_by_iid(state, 117)
    issue_115 = find_issue_by_iid(state, 115)
    issue_117["relatedIssues"].append({"issueId": issue_115["id"], "linkType": "relates_to"})
    issue_115["relatedIssues"].append({"issueId": issue_117["id"], "linkType": "relates_to"})


def solve_task_27(state):
    """Remove blocks relationship between #101 and #102."""
    issue_101 = find_issue_by_iid(state, 101)
    issue_102 = find_issue_by_iid(state, 102)
    issue_101["relatedIssues"] = [r for r in issue_101["relatedIssues"] if r["issueId"] != issue_102["id"]]
    issue_102["relatedIssues"] = [r for r in issue_102["relatedIssues"] if r["issueId"] != issue_101["id"]]


def solve_task_28(state):
    """Create label 'testing' with color #17a2b8."""
    state["labels"].append({
        "id": state["_nextLabelId"],
        "name": "testing",
        "description": "",
        "color": "#17a2b8",
        "textColor": "#ffffff",
        "scoped": False,
    })
    state["_nextLabelId"] += 1


def solve_task_29(state):
    """Create scoped label 'environment::staging'."""
    state["labels"].append({
        "id": state["_nextLabelId"],
        "name": "environment::staging",
        "description": "",
        "color": "#5cb85c",
        "textColor": "#333333",
        "scoped": True,
    })
    state["_nextLabelId"] += 1


def solve_task_30(state):
    """Edit needs-triage label description."""
    label = find_label_by_name(state, "needs-triage")
    label["description"] = "Requires initial assessment, categorization, and priority assignment"


def solve_task_31(state):
    """Change bug label color."""
    label = find_label_by_name(state, "bug")
    label["color"] = "#e74c3c"


def solve_task_32(state):
    """Delete breaking-change label."""
    label = find_label_by_name(state, "breaking-change")
    label_id = label["id"]
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]
    for issue in state["issues"]:
        issue["labels"] = [lid for lid in issue["labels"] if lid != label_id]


def solve_task_33(state):
    """Create milestone v4.4 Release."""
    state["milestones"].append({
        "id": state["_nextMilestoneId"],
        "title": "v4.4 Release",
        "description": "Q3 improvements and stability fixes",
        "startDate": "2026-07-01",
        "dueDate": "2026-09-30",
        "state": "active",
        "createdAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextMilestoneId"] += 1


def solve_task_34(state):
    """Edit Backlog milestone description."""
    ms = find_milestone_by_title(state, "Backlog")
    ms["description"] = "Unscheduled items for future quarterly planning review"


def solve_task_35(state):
    """Close v4.2 Release milestone."""
    ms = find_milestone_by_title(state, "v4.2 Release")
    ms["state"] = "closed"


def solve_task_36(state):
    """Activate v4.0 Release milestone."""
    ms = find_milestone_by_title(state, "v4.0 Release")
    ms["state"] = "active"


def solve_task_37(state):
    """Delete v4.1 Patch milestone."""
    ms = find_milestone_by_title(state, "v4.1 Patch")
    ms_id = ms["id"]
    state["milestones"] = [m for m in state["milestones"] if m["id"] != ms_id]
    for issue in state["issues"]:
        if issue["milestoneId"] == ms_id:
            issue["milestoneId"] = None


def solve_task_38(state):
    """Change v4.3 Release due date."""
    ms = find_milestone_by_title(state, "v4.3 Release")
    ms["dueDate"] = "2026-07-15"


def solve_task_39(state):
    """Create iteration Sprint 28 in Sprint Cycle."""
    cadence = find_entity(state["iterationCadences"], title="Sprint Cycle")
    state["iterations"].append({
        "id": state["_nextIterationId"],
        "cadenceId": cadence["id"],
        "title": "Sprint 28",
        "startDate": "2026-04-14",
        "endDate": "2026-04-27",
        "state": "upcoming",
        "createdAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextIterationId"] += 1


def solve_task_40(state):
    """Create iteration May 2026 in Monthly Planning."""
    cadence = find_entity(state["iterationCadences"], title="Monthly Planning")
    state["iterations"].append({
        "id": state["_nextIterationId"],
        "cadenceId": cadence["id"],
        "title": "May 2026",
        "startDate": "2026-05-01",
        "endDate": "2026-05-31",
        "state": "upcoming",
        "createdAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextIterationId"] += 1


def solve_task_41(state):
    """Create epic 'GraphQL API Layer'."""
    state["epics"].append({
        "id": state["_nextEpicId"],
        "title": "GraphQL API Layer",
        "description": "",
        "state": "opened",
        "authorId": state["currentUser"]["id"],
        "labels": [],
        "confidential": False,
        "startDate": None,
        "dueDate": None,
        "parentEpicId": None,
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextEpicId"] += 1


def solve_task_42(state):
    """Add performance label to Mobile Responsive Redesign epic."""
    epic = find_epic_by_title(state, "Mobile Responsive Redesign")
    perf = find_label_by_name(state, "performance")
    if perf["id"] not in epic["labels"]:
        epic["labels"].append(perf["id"])


def solve_task_43(state):
    """Close Documentation Revamp epic."""
    epic = find_epic_by_title(state, "Documentation Revamp")
    epic["state"] = "closed"


def solve_task_44(state):
    """Reopen Data Export/Import Feature epic."""
    epic = find_epic_by_title(state, "Data Export/Import Feature")
    epic["state"] = "opened"


def solve_task_45(state):
    """Create child epic under API v3 Migration."""
    parent = find_epic_by_title(state, "API v3 Migration")
    state["epics"].append({
        "id": state["_nextEpicId"],
        "title": "API v3 - Deprecated Endpoints",
        "description": "",
        "state": "opened",
        "authorId": state["currentUser"]["id"],
        "labels": [],
        "confidential": False,
        "startDate": None,
        "dueDate": None,
        "parentEpicId": parent["id"],
        "createdAt": "2026-03-18T12:00:00.000Z",
        "updatedAt": "2026-03-18T12:00:00.000Z",
    })
    state["_nextEpicId"] += 1


def solve_task_46(state):
    """Change Dark Mode Implementation start date."""
    epic = find_epic_by_title(state, "Dark Mode Implementation")
    epic["startDate"] = "2026-03-15"


def solve_task_47(state):
    """Add tech-debt list to Development Board."""
    board = find_board_by_name(state, "Development Board")
    label = find_label_by_name(state, "tech-debt")
    # Push closed list position up
    closed_list = next((l for l in board["lists"] if l["type"] == "closed"), None)
    pos = closed_list["position"] if closed_list else len(board["lists"])
    if closed_list:
        closed_list["position"] += 1
    board["lists"].append({
        "id": state["_nextBoardListId"],
        "type": "label",
        "labelId": label["id"],
        "title": label["name"],
        "position": pos,
    })
    board["lists"].sort(key=lambda l: l["position"])
    state["_nextBoardListId"] += 1


def solve_task_48(state):
    """Remove Review list from Development Board."""
    board = find_board_by_name(state, "Development Board")
    board["lists"] = [l for l in board["lists"] if l["title"] != "Review"]
    for i, lst in enumerate(board["lists"]):
        lst["position"] = i


def solve_task_49(state):
    """Add needs-triage list to Bug Triage Board."""
    board = find_board_by_name(state, "Bug Triage Board")
    label = find_label_by_name(state, "needs-triage")
    closed_list = next((l for l in board["lists"] if l["type"] == "closed"), None)
    pos = closed_list["position"] if closed_list else len(board["lists"])
    if closed_list:
        closed_list["position"] += 1
    board["lists"].append({
        "id": state["_nextBoardListId"],
        "type": "label",
        "labelId": label["id"],
        "title": label["name"],
        "position": pos,
    })
    board["lists"].sort(key=lambda l: l["position"])
    state["_nextBoardListId"] += 1


def solve_task_50(state):
    """Mark notification about assignment to #105 as read."""
    notif = next(
        n for n in state["notificationFeed"]
        if "Marcus Johnson assigned you to issue #105" in n.get("message", "")
    )
    notif["read"] = True


def solve_task_51(state):
    """Mark all notifications as read."""
    for n in state["notificationFeed"]:
        n["read"] = True


def solve_task_52(state):
    """Change notification level to watch."""
    state["notificationSettings"]["level"] = "watch"


def solve_task_53(state):
    """Enable email notification for closed issues."""
    state["notificationSettings"]["email"]["closedIssue"] = True


def solve_task_54(state):
    """Disable email notification for new comments."""
    state["notificationSettings"]["email"]["newComment"] = False


def solve_task_55(state):
    """Delete ready-for-dev label (side effect: remove from issues)."""
    label = find_label_by_name(state, "ready-for-dev")
    label_id = label["id"]
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]
    for issue in state["issues"]:
        issue["labels"] = [lid for lid in issue["labels"] if lid != label_id]


def solve_task_56(state):
    """Delete Backlog milestone (side effect: clear from issues)."""
    ms = find_milestone_by_title(state, "Backlog")
    ms_id = ms["id"]
    state["milestones"] = [m for m in state["milestones"] if m["id"] != ms_id]
    for issue in state["issues"]:
        if issue["milestoneId"] == ms_id:
            issue["milestoneId"] = None


# ---------------------------------------------------------------------------
# Solver registry
# ---------------------------------------------------------------------------

SOLVERS = {f"task_{i}": globals()[f"solve_task_{i}"] for i in range(1, 57)}


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------

def find_free_port(start=9500):
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start + 200}")


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


def seed_server(server_url, seed_state):
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# Task execution
# ---------------------------------------------------------------------------

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
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"
        time.sleep(0.1)

        # 2. Read clean seed state
        state = deepcopy(seed_state)

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Function-task sanity check")
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
